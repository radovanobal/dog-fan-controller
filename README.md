# Dog Fan Controller

A PWM controller for two Noctua NF-A14 PWM fans, using an ESP32-C3 SuperMini
and an external SHT4x temperature and humidity sensor.

## Licence and attribution

Copyright © 2026 **Appicanis, Radovan Obal s.p.**

The original hardware design and accompanying design documentation are
licensed under **CERN-OHL-P-2.0**. See [LICENSE](LICENSE) for the complete
licence and [NOTICE](NOTICE) for attribution, source location and scope.

You may use, modify, manufacture and sell the design, including commercially.
You do not have to publish your modifications. When redistributing design
materials, retain the applicable notices and provide the licence; when
redistributing modified design materials, also identify and date your changes.
When supplying physical products, ensure recipients can access the applicable
notices, as required by section 4 of the licence. We impose no additional
requirement for prominent branding or credit on a product or sales page.

Original design: **Appicanis, Radovan Obal s.p.**  
Source: <https://github.com/radovanobal/dog-fan-controller>

Third-party materials retain their own licences. Firmware and standalone
software require their own explicit licence; the hardware licence above
does not automatically apply to them.

## Open on another machine

Install **KiCad 10** with its standard symbol, footprint and 3D model libraries,
clone this repository, then open `Fan Controller.kicad_pro` in KiCad.
No personal library configuration or custom path variables are required.

The project library tables explicitly reference KiCad's standard libraries using
`KICAD10_SYMBOL_DIR` and `KICAD10_FOOTPRINT_DIR`. Custom dependencies are included
in `custom_footprints.pretty/`, `Fan_Controller.pretty/`, `symbols/` and
`3dmodels/`, and use `${KIPRJMOD}` paths relative to the checkout. The two
root-level symbol libraries are also registered in the project table. Standard
3D models use KiCad's `KICAD10_3DMODEL_DIR` setting.

When adding a custom part, include its symbol, footprint and any 3D model in the
repository and update the project library tables. Avoid absolute paths or
libraries registered only in your personal KiCad settings.

## Manufacturing preparation

JLCPCB fabrication and draft assembly outputs, order settings and review status
are in [manufacturing/jlcpcb](manufacturing/jlcpcb/README.md). Regenerate exports
with `python3 tools/prepare_jlcpcb.py` using KiCad 10.
