# QuadWild with Bi-MDF

Skin topology uses the Windows x64 0.0.2 bundle from
https://github.com/cgg-bern/quadwild-bimdf/tree/v0.0.2 under GPL-3.0.
The original LICENSE.txt and configuration files accompany the runtime bundle.
Exact file fingerprints and release URL are in `anthroforge/data/quadwild.json`.
Install with `python tools/setup_quadwild.py` in the project environment.
There is no runtime downloader or backend substitution.

The standalone FLOW kernel derives from maintained AnthroForge addon code; source
fingerprints and adaptation notes are in `native/migration/topology/`.
The bundle's known Windows quantizer exit 2147483651 is accepted only when its
quad mesh validates and remains an explicit warning.
