# Attachment parity and audited workflows - 0.3.4

- Task branch: `codex/parity-workflows-034`
- Integration branch: `main`
- Starting revision: `1acb8ae`
- Status: in progress; NOT release qualified or merge ready
- Active writer: desktop implementation session
- Last updated: 2026-10-24

## Outcome and confirmed decisions

Implement F01-F03 from [parity findings](../addon_parity_findings.md) and D01-D12
from [the audit](../addon_functionality_audit.md), through desktop and shared API.
Preserve geometry, attachment intent, original assets and unrelated root __init__.py.
Use native numerical work, one coordinator, <=15-line functions, background validation,
task checkpoints and one canonical release distribution after qualification.

- Automatic Fiber supports plus explicit inclusions/exclusions; routing is separate.
- Replacement review preserves reliable references and requires explicit approval for
  rebinds, incompatible setting changes and discarded fields/masks.
- Presets reset inflation, relaxation and preset-owned constraints; preserve custom
  fields/regions, source, classification, cropping and stacking relationships.
- SCP splitting keeps first identity/children; other segments become siblings.
- Tissue retargeting may cross construction families after compatibility review.
- Quick Fiber defaults ROUTED, binds each clicked point, Shift-click continues and plain
  click after the first finishes. One undo; no orphan draft on cancellation/failure.
- Fiber display thickness uses world units, independent of numerical clearance.
- Planned release 0.3.4; schema 6 now reads 4/5/6 without blanket startup evaluation.

## Implemented checkpoints

- F02: fresh Blender inventories capture effective Backsolve and unset-state evidence.
  Migration rejects old raw-only inventories and configures both wrappers and drivers.
  Standalone Backsolve default stays off.
- F03: owner capture retains a reference geometry asset/material record through pending
  contexts, history and saves. Native backsolve resolves material provenance instead of
  rereading a recycled Boolean face index. A native migration adapter transfers original
  source polygon centers while preserving baseline pose.
- Actual Thumb +5% thickness: effective policy alone gives .00059519 max surface error;
  policy plus source polygon anchor gives 7.80384e-6, versus original .00628144. Fixed
  camera renders were inspected: corrected shape matches source at baseline precision.
- D01: authored automatic/includes/excludes support policy, API and searchable surface
  chooser/virtualized override list. Mandatory pin targets cannot be excluded; tissue
  supports remain independent from routing obstacles. Shared copy/dependency policies
  and schema-6 persistence include intent.
- D02: Rebind All retains current resolved positions/targets. On-demand Issues checks
  validate pins natively in batches and propose qualified current-position rebindings.
  Paginated review supports selected approval; all proposals validate before one atomic
  edit. Stale plans reject; existing Issues repair tracking verifies publications.
- D03: signed Normal Offset edits retain material identity. Workers resolve batched
  frames and place controls/handles natively before path evaluation. Manual pending
  intent round trips; ordinary point movement supersedes its pending offset intent.
- D04: saved use_warm_start and authoritative cold Recalculate from planner. Cold intent
  belongs to the job, survives retries and is attributed in the profiler. Accepted output
  remains displayed until success; settings and routing collision rules are preserved.
- D12: surface.source_ids plus one-action ordered source selection, with a shared batch
  selection mechanism. No authored edit/undo entry or simultaneous multi-curve editing.

## Pending shoulder decision and evidence

F01 is NOT fixed. Source tangent/point transfer reduces Hook position error from 1.12826
to .11088 but does not establish parity. Flow-point transfer does not reduce the residual;
outer-reference transfer worsens it to .4052 and was rejected. Hook membership and actual
body endpoint continuity are intact. Scapula Shrinkwrap is a different dependency branch.

The source builds separate loft strips; the app welds boundaries. Solidify therefore
uses different seam normals. At the actual source anchor, corresponding outer vertices
are .000145 apart; inner offset vectors differ .131804 before the edit and .006680 after.
Source cyclic guides are resampled to 64 then factor sampled into 65 loft columns.
The dominant observed difference is shell seams, not merely sample count.

An asynchronous user question is PENDING: preserve source strip boundaries for this
migrated Ribs only (welded stays default), or keep welded Ribs with a documented response
mismatch? Do not assume an answer or change the welded contract silently. Continue
independent work; qualify full frame/correspondence transfer after that decision.

## Verification and remaining qualification

- Full pytest: 2,076 passed in 148.24s at the D01-D04 checkpoint; later source-selection
  tests and existing interaction/architecture tests: 19 passed. Ruff and mypy pass.
- Windows native build and all five native tests pass. Full native style passed before
  later native additions; targeted material/curve/shortcut clang-tidy also passed.
- Extended offscreen Fiber acceptance passes support toggle, Normal Offset, Rebind All,
  scan/select/apply repair modal and existing binding/gesture behavior, with no warnings.
- Extended offscreen surface acceptance passes ordered source selection plus creation,
  Realign, inspector editing, undo and geometry staging. An obsolete exact-tooltip text
  assertion was replaced with selection/action behavior.
- construction_editor_acceptance still reports a UiNumberField.propertyState binding
  loop. Reproduced with the support component removed in an ignored QML copy; not hidden
  or claimed passed. Investigate its query/notification boundary before final release.
- Corrected Thumb profiler report is complete, with no reported losses. One headless
  update retained about 1.059 seconds; material capture .415ms, material backsolve .212ms.
  These are single-run measurements, NOT a speedup or desktop responsiveness claim.
  Profiler inventory cost remains separately attributed; do not subtract it exactly.
- Full development gate, broader parity/lifecycle cases, profiler workloads and portable
  package are still pending. Package version remains 0.3.3; no release or main merge.

## Immediate next actions

1. Resolve F01 after the pending seam decision; compare unchanged baseline and Ribs=3
   analytically and visually. Preserve originals and no silent mesh fallback.
2. Implement D05 active length weight and meaningful interactive/final budgeting. Native
   routing currently steps one accepted iteration between cancellation checks; do not
   add inert controls or weaken collision validation. Custom/PIQP defaults must match.
3. Implement D06 connected SCP splitting and D07/D08 replacement assessment/approval,
   preserving reliable references and rejecting stale assessments atomically.
4. Implement D09 preset ownership/application, D10 direct Fiber placement and D11 native
   world-radius presentation/picking. Never substitute pixel linewidth for world radius.
5. Resolve the recorded GUI metadata binding loop without regressing 0.3.3 targeted
   notification performance; verify with the profiler and offscreen acceptance.
6. Qualify remaining geometry, undo/save/resources and actual 96-muscle assembly. Save a
   final corrected copy outside build only after complete acceptance; no mirrored muscles.
7. Final docs/notices/version, full gates, canonical dist/0.3.4/AnthroForge.dist and source
   archive, then validated merge/push. Do not present this task as complete beforehand.

## Recovery inputs

Local-only evidence: build/parity-workflows-034 (ignored). Files include fresh
`effective-inventory.json`, `policy-repaired.anthroforge`, `anchor-repaired.anthroforge`,
plans, actual Thumb snapshots, `thumb-anchor-distances.json`, `ribs-shell-seams.json`,
`thumb-correction.png`, and `thumb-correction.afprofile.zip`.

Original paired input:
E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge
and E:/development/WIP_models/shortcut_update_parity_20261023/matching_96_muscles.blend.
Earlier evidence remains in build/shoulder-thumb-parity. Preserve source hashes recorded
there. External anatomy/binary evidence is not available from Git alone during an outage.
The addon worktree contains unrelated local edits; do not modify it.

## Recovery checkpoint: active routing execution controls

D05 now exposes typed length_weight (default .9) and checkpoint_steps (default 1),
separate from the existing total accepted-step cap. Checkpoints count SOLVER TRIALS,
not accepted updates; native kernel inspection established this distinction. Both QP
backends use the selected objective weight, regularization scale and initial penalty.
Old C ABI entrypoints retain .9/1 defaults; additive configured entrypoints carry settings.
Inspection always checkpoints each trial for complete evidence. Production report measure
5 records actual checkpoint count; no intermediate viewport preview is claimed.

Snapped-cube 128-point Fiber, Custom/PIQP: quantum 1 vs 4 gives bit-identical paths and
counters, with 54 vs 14 checkpoints at weight .9. Weight 0 changes both routes while
independent collision checks remain clear. 67 focused routing/parity/warm/inspection/
architecture tests pass; native build and all five native tests pass; Ruff passes.
Full integrated gate and remaining D06-D11 workflows are NOT complete.
