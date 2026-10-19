# Unified tissues 0.2.2

- Task branch: `codex/unified-tissues-022`
- Integration branch: `main`
- Starting revision: `6f33380660c9421585b0898b068d33b4f5232fd3`
- Status: in progress; implementation and release qualification incomplete
- Last updated: 2026-10-19, Europe/Bucharest
- Active writer: desktop chat, direct work (no delegated writers)

## Outcome and acceptance

Implement the user-approved 0.2.2 plan: unified TissueVCP, attached Point/Anchor
and Surface/Membrane construction, native inflation/relaxation/stacking, shared
attachments, desktop/headless workflows, schema 4 and a qualified portable release.
Keep the current 0.2.1 distribution intact until qualification. See the forthcoming
[specification](../specification_022.md) and [implementation plan](../implementation_022.md).

## Confirmed decisions

- One TissueVCP; anatomical labels and presets do not select algorithms.
- Shared Anchor/Fiber/Membrane sources; explicit independent copies.
- Bone anchoring may be indirect through other tissues.
- Stacking requires surface-based providers and receivers; capability contract
  must allow future base adapters without changing the tissue entity.
- Preserve per-part/side settings, current unstacked display on stacking failure,
  and the final-surface dependency barrier; no silent successful fallback.
- Schema 4 only; reject earlier formats, including 0.2.1 schema 3.
- No mirroring, skin, Blender conversion, reconstruction/fitting, or dynamics.
- Preserve scheduler/history/save/startup/export semantics and 15-line functions.

## Current state

Inspected addon production contracts and current standalone boundaries. The
registry, anatomical queries and attachment candidate paths still assume SCPs.
Numerical ports must include remaining Python mesh/field preparation, not just
the already-native solvers. Existing addon kernels, PIQP 0.6.4 and qualification
fixtures are migration references; Blender is not a runtime dependency.

Specification, migration inventory, implementation plan and active documentation
links are written. Typed Point/Anchor/Membrane/TissueVCP contracts, schema 4,
stage-result ownership and role-aware accepted surface providers are implemented.
All-Fiber surface creation now produces a Membrane. Point creation/editing and
independent Anchor capture/rebind use shared commands, native binding kernels,
the existing coordinator and undo history. Parent movement resolves retained
bindings; deletion protection and workspace association include Anchors.

Point/Anchor desktop creation, inspector, native picking and explicit rebind are
integrated. Membranes retain the existing Surface inspector and staged display.
Tissue phase revisions distinguish base/rest/intrinsic/final invalidation; topology
locks traverse construction consumers through Membranes to tissue attachments.

Native meshes now retain validated material grids and welded branch vertex identities;
deformation, finalization, memory accounting and project storage preserve them. This
supplies exact source correspondence for the upcoming tissue evaluators.

Ordinary loft inflation now uses pinned addon kernels for Distributed, control-point
falloffs and Section Profile directions. Nine addon-generated fixtures match at 1e-12.
Native accepted-grid refinement provides interior samples without source mutation.
Coordinated base/rest/intrinsic/final jobs, phase-aware publications, tissue creation
and inflation commands work for ordinary one-sided loft tissue with stacking disabled.
Five workflow/architecture checks pass, including source motion, base reuse, transform
rejection, deletion/undo and schema-4 stage round trips. Other intrinsic strategies
and stacking currently fail explicitly; they must be completed before release.
Desktop ordinary-loft tissue creation/selection and inspector are now connected.
Tissues appear in Anatomy, not Construction; generated transforms are disabled.
`tools/tissue_editor_acceptance.py` passes full-QML offscreen controls without warnings;
inspected `build/022-tissue/tissue-inspector.png` (offscreen platform has no 3D view).
`tools/tissue_scene_acceptance.py` separately renders the inflated tissue via hidden
GPU texture, with matching hover/click selection; inspected `tissue-gpu.png`.
No desktop windows or user input were used. These qualify only the current ordinary
loft increment, not the entire planned tissue UI or geometry workflow.
Desktop/cancellation checkpoint full suite: **988 passed**, 475 Qt warnings,
32.28 seconds. Active native Section Profile cancellation finishes within the two-second
test deadline; pinned source bytes are checked, and Manual tissue evaluation retains its
previous output until explicit evaluation. Formatting corrected after the gate's first pass.
Inflation/stage checkpoint full suite: **983 passed**, 335 Qt warnings, 31.25 seconds.
Configured mypy, ruff, formatting, three native CTests and changed-adapter clang-tidy
checks pass. No runtime release or full tissue qualification is implied.

Runtime integration remains incomplete: generalized Fiber roles, intrinsic numerical ports, stacking,
full GUI and release qualification are still required. No 0.2.2 release is claimed.
Accepted tissue bases now distinguish an Anchor frame, retained Fiber path and Membrane
mesh without synthetic point/curve meshes. Native outputs retain validated sparse material
correspondence, side/part labels and source faces across deformation, finalization,
memory accounting and schema-4 storage. Twenty base/workflow checks and seven material-map/
architecture checks pass; configured mypy, ruff, formatting and native build/CTest pass.
Radial, sweep and normal-shell kernels are the next increment; they are not yet connected.
Unrelated untracked root `__init__.py` is preserved.

## Verification

Baseline `uv run --no-sync pytest -q`: **941 passed**, 307 existing Qt deprecation
warnings, 31.89 seconds on Windows. `git diff --check` passed for documentation.
Baseline main matched origin/main before branching.
Foundation full suite: **951 passed**, 307 existing warnings, 30.18 seconds.
Next full suite after attached-point operations/output dispatch: **957 passed**,
307 existing warnings, 34.41 seconds. Point/Anchor lifecycle checks
exercise capture, parent motion, explicit rebind, undo/redo, deletion protection
and persistence. Shared provider and output dispatch changes still require the
next complete regression run. `tools/point_editor_acceptance.py` passes full-QML
creation, explicit rebind and undo without warnings. Its offscreen platform does
not render the 3D viewport; inspected UI capture at `build/022-points/anchor-inspector.png`.
Separately `tools/point_scene_acceptance.py` passes GPU texture-only rendering and
native picking with no visible window; inspected `build/022-points/point-gpu.png`.
Full tissue geometry parity and release acceptance remain pending.
Point/UI foundation full suite: **964 passed**. Material correspondence full suite:
**969 passed**, 335 Qt deprecation warnings, 31.24 seconds. Native build and three CTest
contracts pass; changed native adapters pass the native function-length check. An
over-broad explicit mypy invocation included intentionally untyped desktop modules;
the repository gate uses its configured scopes instead.
Required: development gate, geometry parity, lifecycle, headless, offscreen UI,
profiler and portable acceptance, followed by ownership/coupling review.

## Next actions

1. Finish attached-construction desktop entry points and role-aware consumers.
2. Integrate intrinsic construction, attachment chains and stacking native kernels.
3. Complete focused tissue inspectors and editing tools.
4. Qualify and release, then validated merge/push. Do not merge partial checkpoints.

## Recovery inputs

Standalone checkout: `E:/development/anthroforge`. Addon reference:
`C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
Use the existing Windows/cloud setup guides. Original anatomy and source .blend
fixtures remain external; commit compact extracts and provenance only. Validation
must stay background/offscreen, without desktop input or visible test windows.
