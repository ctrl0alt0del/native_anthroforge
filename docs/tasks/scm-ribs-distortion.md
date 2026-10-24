# Sternocleidomastoid distortion after Ribs Top Radius

- Task branch: `codex/scm-ribs-distortion`
- Integration branch: `main`
- Starting revision: `4ff1ef8`
- Status: investigation in progress
- Last updated: 2026-10-25, Europe/Bucharest
- Active writer: local Codex

## Outcome

Reproduce the reported zigzag/stretching of `Sternocleidomastoid.L continuous belly`
after Ribs Top Radius becomes 3. Distinguish propagation/correspondence defects from
intrinsic inflation/stacking limitations before proposing changes. Preserve source WIP
projects and existing attachments. Do not change attachment/algorithm behavior before
explaining the observed cause and proposed approach to the user.

## Inputs and next steps

Baseline assembly: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
Use read-only package adoption, existing profiler, stage inspection and hidden GPU captures.
Trace bindings -> paths -> surface -> rest -> intrinsic -> final, comparing full propagation
with explicit reevaluation and stage-isolated evaluation. No production changes yet.
Evidence belongs under `build/scm-ribs-distortion/`. No desktop takeover or source-file save.
Preserve unrelated root `__init__.py` and unfinished 0.3.4 branch.
