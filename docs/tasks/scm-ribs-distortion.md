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


## Observed evidence

Exact tissue ID `fc8df927-2290-4af2-b8e9-882697a8733e`, membrane
`b4e00a6c-5071-4e9e-b2b8-00446a2562fa`; three POLYLINE Fibers, each 73 samples.
Ribs edit reproduces distortion at paths/base, before SECTION_PROFILE inflation.
Stacking is disabled; relaxation NONE. Base maximum edge grows .297 -> 1.992.
Explicit reevaluation produces byte-identical geometry at all four tissue stages.
Authored points, captured owners/weights/bindings and bind path are unchanged.
Middle Fiber: samples 66–71 follow Ribs at weight 1, sample 72 is hard-pinned Spine.
Neighboring Ribs frames alternate strongly; retained offsets around .73–.76 amplify
rotation differences. Automatic support mapping and short terminal blend are implicated.
Existing native weights match addon `core/vcp/fiber_node_attachment_weights.py`.
Historical matching-addon capture `shortcut_update_parity_20261023/blender/SHORTCUT_4`
already has a 2.003 maximum adjacent middle-Fiber gap (app current 1.992), versus .171
baseline. This is existing captured evidence, not a newly executed Blender test.
No production code/attachment behavior changed. Diagnostic ablations/visual inspection next.
