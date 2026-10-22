# Evidence and reproduction

- [Findings and proposed boundaries](../../shortcuts_030_research.md)
- [All shortcuts and exact driver formulas](inventory.md)
- [Machine-readable inventory](inventory.json)

The files are definition evidence, not a migration or geometry acceptance result.
The inventories are available in Git; the source `.blend` files remain local assets.
Both source hashes are recorded in the inventories. No meshes or full muscle payloads
are included. The small captured curve controls document the observed Bézier construction.

From the standalone repository root, with Blender 5.0.1 and the original addon installed
at the path in `extract_blender.py`, run in PowerShell:

```powershell
New-Item -ItemType Directory -Force build/shortcuts-030 | Out-Null
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' --background --factory-startup --disable-autoexec --python-exit-code 1 --python docs/research/shortcuts_030/extract_blender.py -- E:/development/WIP_models/skeleton_comb_base.blend build/shortcuts-030/skeleton_comb_base.json
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' --background --factory-startup --disable-autoexec --python-exit-code 1 --python docs/research/shortcuts_030/extract_blender.py -- E:/development/WIP_models/skull_muscles.blend build/shortcuts-030/skull_muscles.json
.venv/Scripts/python.exe docs/research/shortcuts_030/summarize.py
```

The extractor registers only SCP/shortcut property types so saved RNA groups can be
read. It does not register the addon's load handlers, apply shortcut changes or save
the file. Automatic scripts are disabled by the required CLI flags. Driver expressions
are read as strings; the FCurve mapping probe evaluates only its scalar mapping.
The captured resolved values are inspection-time values, not a guarantee about dynamic
dependency evaluation after editing. The audit used addon revision
`fae36aba1b208676cf21d7c4a78a20d5b1f68c66`.

Driver reachability includes explicit SINGLE_PROP references and relevant own scale
components of the two TRANSFORMS references. World-space transform values additionally
depend on the source object's parents. Modifier geometry, attachments and Geometry Nodes
links are not FCurve edges and are not claimed as fully inventoried dependencies.

Checks performed: 116/116 target paths and values resolve; owner references and driver
IDs resolve; all 40 driver channels are recorded; 39 scripted drivers report simple
expressions and one is AVERAGE; source hashes unchanged; extraction/generation functions
remain within 15 physical lines. No app rebuild or full regression gate is warranted
for this research-only change. Formula evaluation/geometry parity remains future work.
