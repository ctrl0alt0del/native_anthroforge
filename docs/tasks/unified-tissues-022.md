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

Runtime integration remains incomplete: Point/Anchor desktop tools, tissue phase
revision policies, generalized Fiber roles, intrinsic numerical ports, stacking,
full GUI and release qualification are still required. No 0.2.2 release is claimed.
Unrelated untracked root `__init__.py` is preserved.

## Verification

Baseline `uv run --no-sync pytest -q`: **941 passed**, 307 existing Qt deprecation
warnings, 31.89 seconds on Windows. `git diff --check` passed for documentation.
Baseline main matched origin/main before branching.
Foundation full suite: **951 passed**, 307 existing warnings, 30.18 seconds.
Subsequent Point/Anchor lifecycle and architecture checks: **8 passed**. These
exercise capture, parent motion, explicit rebind, undo/redo, deletion protection
and persistence. Shared provider and output dispatch changes still require the
next complete regression run; desktop/geometry parity acceptance is pending.
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
