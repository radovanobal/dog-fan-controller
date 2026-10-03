# JLCPCB preparation — Dog Fan Controller

Prepared 2026-09-17 with KiCad 10.0.5. This package is for quotation and review;
no order has been submitted. Assembly part availability and vendor orientation
matching are not yet verified.

## Files to upload

- `Dog-Fan-Controller-Gerbers.zip`: 11 Gerber layers plus separate PTH and NPTH
  Excellon drill files, all using the same absolute origin. No drawings or
  validation reports are included in the ZIP.
- `assembly/BOM.csv`: draft top-side assembly BOM, 40 components / 26 part numbers.
- `assembly/CPL.csv`: matching 40 placements in millimetres, with KiCad rotations
  normalized to 0–360 degrees. Coordinates use the same absolute origin as the
  fabrication data; negative Y coordinates are intentional.
- `assembly/excluded-parts.csv`: nine DNP components and four mechanical holes.
  F1, J1–J7 and U1 are excluded from JLCPCB assembly according to the board flags.
  U1 is explicitly marked for hand population. Confirm the other exclusions in
  the assembly preview; DNP here does not mean these parts are unnecessary for
  the completed controller.
- `previews/`: independent Gerber renders of the top, bottom and inner layers.
- `reports/`: DRC, ERC, drill inventory, Gerber parsing results and source/output
  SHA-256 hashes. These are review records, not fabrication layers.

## PCB order settings

| Setting | Value |
|---|---|
| Layers | 4: F.Cu → In1.Cu → In2.Cu → B.Cu |
| Finished outline | 33 × 96 mm (outline centreline dimensions) |
| Material / nominal thickness | FR-4 / 1.6 mm |
| Outer copper | 1 oz |
| Inner copper | 0.5 oz — accepted for the stated fan/controller load |
| Stackup | Standard JLC04161H-7628 / published “No requirement” construction |
| Impedance control | No controlled-impedance requirement identified in this design |
| Via covering | Tented on both sides as exported |
| Holes | 85 plated, including 38 vias; 7 non-plated |
| Smallest drill / via diameter | 0.30 mm / 0.60 mm |
| Minimum routed track width | 0.20 mm |
| Quantity, solder-mask colour, finish | Still to select in the quotation |

The board metadata now follows JLCPCB's published construction: 35 µm outer
copper, 15.2 µm inner copper, two 0.2104 mm prepregs and a 1.065 mm dielectric
core. Overall board thickness remains nominally 1.6 mm. Published nominal layer
thicknesses and solder mask do not sum to exactly 1.6000 mm; factory finished
thickness tolerance applies. Confirm the construction offered in the quote.

## Copper/current assessment

The stated load is the two fans plus the buck-powered controller, with no
additional expansion-header power loads specified. The README identifies
standard 12 V Noctua NF-A14 PWM fans; Noctua rates these at 0.13 A maximum each
(0.26 A combined). This assumption does not cover industrialPPC or 5 V variants.

The current layout has a continuous GND island on In1.Cu, and separate continuous
3.3 V and protected-input-12 V islands on In2.Cu. The protected-input plane feeds
the two buck converters. Fan-rail and 5 V output distribution is routed on the
outer layers, which retain 1 oz copper. Zone thermal spokes are 0.5 mm wide.

For scale, using copper resistivity 1.724e-8 Ω·m at 20°C, a 100 mm-long,
5 mm-wide strip of 15.2 µm copper has R ≈ 22.7 mΩ. At 2 A this is approximately
45 mV drop and 91 mW loss; at 60°C resistance rises to about 26.2 mΩ. The main
planes are much wider, apart from local pad/via connections. This illustrative
strip calculation and inspection support using standard inner copper for the
stated load. It is not an extracted resistance network or a temperature-rise
simulation, and does not rate the entire assembly for 2 A continuous output from
each regulator. Regulator cooling, external traces, vias, fuse coordination and
transient performance have separate limits. Check temperatures and rail voltages
on the first powered prototype under maximum intended load.

## Verification and remaining review

- Current project DRC: zero board violations and zero unconnected items.
- ERC: zero violations.
- Schematic parity: four extra-footprint notices for mechanical mounting holes
  H1–H4, with no electrical component mismatch.
- DRC uses the project's configured checks. `reports/drc.json` lists ignored
  checks; this is not a blanket manufacturer DFM certification.
- Independent Gerbonara parsing recognizes four copper layers and all technical
  layers, with 85 PTH and 7 NPTH drill hits. Gerber outlines align with the board
  and drill coordinates. KiCad's 0.05 mm outline stroke makes the rendered
  bounding box 33.05 × 96.05 mm; the intended cut follows its 33 × 96 mm centreline.
- No copper routing or component placement was changed while preparing exports;
  only stackup material/thickness metadata changed.
- Check the JLCPCB Gerber preview and layer order before accepting the quote.
- Review silkscreen legibility: the R9/R10 labels are crowded in the top preview.
- Confirm each LCSC number against the manufacturer part, package, ratings and
  live assembly stock. The supplied IDs are copied from the design, not verified
  against current inventory. No substitutions have been made.
- Review component origins and rotations in JLCPCB's placement preview,
  especially U2–U4, Q1, D1–D3, C3 and C19. KiCad rotation conventions can differ
  from the vendor library. No undocumented rotation offsets were applied.
- Final quantity, finish, colour, assembly scope, and any tooling rails/fiducials
  required by the selected assembly service remain quotation decisions.

## Regenerate

Install KiCad 10 and Python 3, then run from the repository:

```sh
python3 tools/prepare_jlcpcb.py
```

Use `--kicad-cli /path/to/kicad-cli` when it is not on PATH. The script runs DRC
and ERC, exports Gerbers/drills/positions, rebuilds the BOM/CPL and ZIP, and records
source/output hashes. It refuses unexpected DRC/ERC/parity findings and incomplete
assembly IDs. It does not modify source board or schematic files. Previews and
independent parser reports are a separate snapshot and should be refreshed after
geometry edits; they are not regenerated by this export script.

## References checked 2026-09-17

- [JLCPCB KiCad Gerber/drill guide](https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-9)
- [JLCPCB BOM format](https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly)
- [JLCPCB placement format](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly)
- [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- [JLCPCB published stackups](https://jlcpcb.com/impedance)
- [Noctua NF-A14 PWM specifications](https://www.noctua.at/en/products/nf-a14-pwm/specifications)
- [Diodes AP63205Q family](https://www.diodes.com/part/AP63205Q/)
