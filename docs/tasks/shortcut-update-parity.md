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

No parity result or application qualification is claimed by this initial checkpoint.
