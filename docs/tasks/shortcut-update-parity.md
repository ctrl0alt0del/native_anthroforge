# Blender/app shortcut update comparison

- Branch: `codex/shortcut-update-parity`; integration: `main`.
- Starting revision: `8b33df958f3518b43fb10bdbb57ecb896bb87220`.
- Status: investigation in progress, 2026-10-23.
- Scope: scripted comparison of four corresponding shortcut edits on matching bone/muscle assemblies, with explicit unit normalization. No production behavior changes.

## Inputs and acceptance

Standalone: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
Its 96 authored muscles originated in 74 separate Blender sources, recorded by
`docs/tasks/all-muscle-migration.md`. Establish a genuinely matching Blender assembly
before claiming whole-assembly parity. Preserve original files and unrelated root
`__init__.py`; all execution stays background/headless.

Compare baseline and edited geometry, poses, endpoint/binding outcomes, actual
completion and failures. Separate pre-existing construction differences from changed
responses. Geometry uses physical common units; scale/angle controls are not blindly
multiplied by a length conversion. Do not equate differing tessellation with failure
or use nearest-vertex comparison as a substitute for surface distance.

## Next actions

1. Inspect source inventory/import contracts and produce a matched comparison pair.
2. Drive four actual shortcut wrappers and wait for both update pipelines.
3. Export analytical evidence, investigate discrepancies, and record limits/results.

## Checkpoint: comparison inputs and captures

Scripts `tools/shortcut_parity_*.py` freeze the 74 donor groups, compose a separate
native Blender assembly, invoke real shortcut actions, export world geometry and
compare native batched nearest-surface distances (vertices plus triangle centroids).
Baseline-qualified vertex displacement and indexed Fiber/endpoint response are
reported separately. Large outputs are local-only at
`E:/development/WIP_models/shortcut_update_parity_20261023/`.

Matched inventory: 59 SCP instances, 96 authored tissues, 326 Fibers. Opposite-side
SCPs are reported separately because the app intentionally has independent copies.
Blender scene scale and app canonical scale are both 1; the source addon root has
no declared physical-unit contract, which must remain explicit in interpretation.

Cases: Ribs Top Radius 3; Humerus scale 3.1134088039398193; Radius scale
2.5114212036132812; Thumb radius 0.07350002229213715. The last three are baseline
times 1.05, rounded once to representable Blender floats and supplied identically
to both runtimes. Every case starts from the saved baseline.

All four app cases completed without scheduler errors. Blender baseline capture
completed but its combined FDS radial source is missing (two invalid bindings).
Investigate the original donor independently; do not silently call this parity.
Other baseline differences include intentional skeleton construction approximations.
Blender edited captures and final analytical interpretation remain in progress.
