#!/usr/bin/env python3
"""Export JLCPCB review files using KiCad 10 CLI and Python's standard library.

Run from any directory: python3 tools/prepare_jlcpcb.py --kicad-cli /path/to/kicad-cli
No source design files are modified. Assembly rotations require vendor preview review.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / 'Fan Controller.kicad_pcb'
SCHEMATIC = ROOT / 'Fan Controller.kicad_sch'
OUT = ROOT / 'manufacturing' / 'jlcpcb'


def parse(text):
    tokens = iter(re.findall(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]', text))
    def node():
        result = []
        for token in tokens:
            if token == ')':
                return result
            if token == '(':
                result.append(node())
            elif token.startswith('"'):
                result.append(token[1:-1].replace('\\"', '"').replace('\\\\', '\\'))
            else:
                result.append(token)
        raise ValueError('Unclosed expression')
    assert next(tokens) == '('
    return node()


def children(node, tag):
    return [x for x in node if isinstance(x, list) and x and x[0] == tag]


def write_csv(path, header, rows):
    with path.open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.writer(stream, lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kicad-cli', default='kicad-cli')
    args = parser.parse_args()
    def cli(*values):
        subprocess.run([args.kicad_cli, *map(str, values)], cwd=ROOT, check=True)
    for name in ['gerbers', 'assembly', 'reports']:
        (OUT / name).mkdir(parents=True, exist_ok=True)
    cli('pcb', 'drc', '--schematic-parity', '--severity-all', '--format', 'json', '-o', OUT/'reports/drc.json', BOARD)
    cli('sch', 'erc', '--severity-all', '--format', 'json', '-o', OUT/'reports/erc.json', SCHEMATIC)
    drc = json.loads((OUT/'reports/drc.json').read_text())
    erc = json.loads((OUT/'reports/erc.json').read_text())
    # Preserve full reports, including ignored checks and mounting-hole parity notices.
    if drc['violations'] or drc['unconnected_items']:
        raise SystemExit('Resolve DRC findings before generating a new package.')
    if any(sheet.get('violations') for sheet in erc.get('sheets', [])):
        raise SystemExit('Resolve ERC findings before generating a new package.')
    parity = drc.get('schematic_parity', [])
    allowed = {'Footprint H1', 'Footprint H2', 'Footprint H3', 'Footprint H4'}
    if any(v['type'] != 'extra_footprint' or any(i['description'] not in allowed for i in v['items']) for v in parity):
        raise SystemExit('Unexpected schematic/PCB parity finding; inspect drc.json.')
    layers = 'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts'
    cli('pcb', 'export', 'gerbers', '-o', str(OUT/'gerbers')+'/', '-l', layers, '--subtract-soldermask', '--check-zones', BOARD)
    cli('pcb', 'export', 'drill', '-o', str(OUT/'gerbers')+'/', '--format', 'excellon', '--drill-origin', 'absolute', '--excellon-units', 'mm', '--excellon-zeros-format', 'decimal', '--excellon-oval-format', 'alternate', '--excellon-separate-th', '--generate-report', '--report-path', OUT/'reports/drill-report.txt', BOARD)
    cli('pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--exclude-dnp', '-o', OUT/'reports/kicad-positions.csv', BOARD)
    tree = parse(BOARD.read_text())
    grouped = defaultdict(list)
    selected = set()
    excluded = []
    for fp in children(tree, 'footprint'):
        fields = {x[1]: x[2] for x in children(fp, 'property')}
        ref = fields['Reference']
        attributes = children(fp, 'attr')
        attributes = attributes[0][1:] if attributes else []
        if 'dnp' in attributes or 'exclude_from_bom' in attributes or ref in {'H1','H2','H3','H4'}:
            reason = 'Mechanical mounting hole' if ref.startswith('H') else 'DNP in board: excluded from JLCPCB assembly'
            excluded.append([ref, fields.get('Value',''), fields.get('MPN',''), fields.get('LCSC',''), reason])
            continue
        if 'smd' not in attributes:
            raise SystemExit(f'{ref}: unexpected non-SMD assembly part; review scope.')
        lcsc, mpn = fields.get('LCSC',''), fields.get('MPN','')
        if not re.fullmatch(r'C\d+', lcsc) or not mpn:
            raise SystemExit(f'{ref}: missing/invalid LCSC number or manufacturer part number.')
        selected.add(ref)
        key = (fields['Value'], fp[1].split(':')[-1], lcsc, mpn, fields.get('MANUFACTURER',''))
        grouped[key].append(ref)
    def natural(ref):
        return re.sub(r'\d+', lambda m: m[0].zfill(6), ref)
    bom = []
    for (value, footprint, lcsc, mpn, manufacturer), refs in grouped.items():
        bom.append([value, ','.join(sorted(refs,key=natural)), footprint, lcsc, mpn, manufacturer, len(refs)])
    bom.sort(key=lambda row: natural(row[1].split(',')[0]))
    write_csv(OUT/'assembly/BOM.csv', ['Comment','Designator','Footprint','LCSC Part #','Manufacturer Part Number','Manufacturer','Quantity'], bom)
    with (OUT/'reports/kicad-positions.csv').open(encoding='utf-8-sig') as stream:
        positions = {row['Ref']:row for row in csv.DictReader(stream)}
    assert selected <= positions.keys(), 'Missing placement coordinates'
    cpl=[]
    for ref in sorted(selected,key=natural):
        row=positions[ref]
        cpl.append([ref, row['PosX'], row['PosY'], row['Side'].capitalize(), f"{float(row['Rot']) % 360:.6f}"])
    write_csv(OUT/'assembly/CPL.csv', ['Designator','Mid X','Mid Y','Layer','Rotation'], cpl)
    write_csv(OUT/'assembly/excluded-parts.csv', ['Designator','Comment','Manufacturer Part Number','LCSC Part #','Reason'], sorted(excluded,key=lambda r:natural(r[0])))
    assert len(cpl)==sum(row[-1] for row in bom)
    files=[OUT/'gerbers'/('Fan Controller-'+name+suffix) for name,suffix in [('F_Cu','.gtl'),('In1_Cu','.g1'),('In2_Cu','.g2'),('B_Cu','.gbl'),('F_Paste','.gtp'),('B_Paste','.gbp'),('F_Silkscreen','.gto'),('B_Silkscreen','.gbo'),('F_Mask','.gts'),('B_Mask','.gbs'),('Edge_Cuts','.gm1'),('PTH','.drl'),('NPTH','.drl')]]
    for f in files:
        assert f.is_file() and f.stat().st_size, f
    archive=OUT/'Dog-Fan-Controller-Gerbers.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for f in files: z.write(f,arcname=f.name)
    manifest={'kicad_version':subprocess.check_output([args.kicad_cli,'version'],text=True).strip(), 'assembly_components':len(cpl),'unique_assembly_parts':len(bom),'excluded_items':len(excluded),'assembly_status':'Draft: vendor part matching, stock and rotation review pending','sha256':{}}
    for f in [BOARD,SCHEMATIC,ROOT/'Fan Controller.kicad_pro',*files,archive,*sorted((OUT/'assembly').glob('*.csv'))]:
        manifest['sha256'][str(f.relative_to(ROOT))]=hashlib.sha256(f.read_bytes()).hexdigest()
    (OUT/'reports/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Created fabrication ZIP; draft assembly: {len(cpl)} components, {len(bom)} part numbers; {len(excluded)} excluded items.')


if __name__=='__main__':
    main()
