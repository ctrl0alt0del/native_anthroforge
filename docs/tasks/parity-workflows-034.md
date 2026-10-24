# Attachment parity and audited workflows - 0.3.4

- Task branch: `codex/parity-workflows-034`
- Integration branch: `main`
- Starting revision: `1acb8ae`
- Status: in progress; NOT release qualified or merge ready
- Active writer: desktop implementation session
- Last updated: 2026-10-24

## Latest recovery state

D01-D12 and F02/F03 are implemented on this task branch. Full development gate passed;
the latest complete pytest run passes 2136 cases. Actual texture-only Fiber rendering,
desktop workflow tools and the read-only 96-muscle display qualifier pass. Source projects
remain untouched. No main merge, package version change or release artifact is delivered.

The only product decision still pending is F01: preserve Blender's separate strip topology
for migrated Ribs (keep welded lofts as the default), or retain welded Ribs and explicitly
accept the remaining source-response difference. A focused user question is pending.
Continue on this branch after that answer; do not assume permission from elapsed time.
Then qualify shoulder baseline/Ribs=3, deliver the corrected assembly, finish packaging
and release/merge checks. Historical checkpoints below retain their original limits.

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
2. D01-D12 and the GUI metadata notification repair are implemented. Continue final
   integration/ownership review, checking desktop and headless lifecycle coverage.
3. Qualify remaining geometry, undo/save/resources and actual 96-muscle assembly. Save a
   final corrected copy outside build only after complete acceptance; no mirrored muscles.
4. Final docs/notices/version, full gates, canonical dist/0.3.4/AnthroForge.dist and source
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

## Inspector notification repair

The recorded construction-editor binding loop is fixed at PropertyQueries: lazy reads
update internal metadata/cache revisions but defer QML map notification to one queued
publication. Controller synchronization still publishes targeted updates immediately.
No periodic timer/polling or document-wide property broadcast was introduced. Direct
queries remain fresh; unchanged accepted geometry still reuses cached metadata.
Regression test verifies fresh lazy reads without synchronous epoch changes and the
subsequent queued publication. Construction, Fiber and Surface offscreen acceptance
all pass with their warning assertions intact; seven metadata/architecture tests pass.
This replaces the earlier recorded construction-editor failure; broader performance
qualification is still pending.

## Connected SCP splitting checkpoint

D06 adds scp.split(entity, points) and the Primitive inspector action operating on selected
interior guide points. As in the addon, supported sources are one open Bezier/Polyline
whole-guide body under an SCP parent, without existing curve deformers or shared consumers.
The first SCP/source identity and children remain; new SCPs are siblings. Other compatible
base/geometry bindings share existing controls with remapped target identities.
Native extraction resolves handles before separating segments and compensates minimum-twist
roll; authored point identities remain on the first segment and copies receive new identities.
Each joint is one Hook following the common parent with two endpoint bindings. Newly created
curves receive fresh result state, never the original curve's accepted source record.
Tests cover coincident endpoints after moving Hook, hierarchy, atomic rejection, undo/redo,
save/open and native shape/roll. Offscreen actual-button acceptance passes without warnings.
Offscreen UI captures did NOT render meshes on this machine; do not claim viewport geometry
acceptance from them. An additional plot of actual native mesh triangles before/after and
Hook movement was inspected (build/parity-workflows-034/split/native-geometry.png); the shape
and connected joint are consistent on this fixture. Interactive desktop acceptance remains
pending. Larger chained/mixed-deformer and incoming attachment cases need broader qualification.

## Existing-tissue preset ownership checkpoint

D09 adds tissue.preset.apply and a direct inspector chooser. It resets inflation across
existing stable parts/sides, relaxation and explicitly PRESET-owned constraints. Source,
classification, smoothing, connector settings, fields, custom regions, crop and stacking
remain. Constraint provenance is serialized; older rows default CUSTOM conservatively.
Explicit edits/rebinds/unlinks promote preset rows to CUSTOM. Preset creation alone tags
its own defaults; public constraint creation cannot spoof managed provenance.
Identical custom/default rows are not duplicated. Obvious contradictory Fixed masks are
rejected. Existing shared capability/topology policies reject incompatible combinations;
field-layout changes reject rather than discard custom weights or captured regions.
Fourteen focused preset/architecture tests pass, including custom-weight package roundtrip,
legacy provenance, custom conflict rejection, one-action undo and preservation. Extended
full-desktop offscreen preset acceptance passes direct existing-tissue chooser as well as
Layer/Pouch creation and Make Independent. Ruff and configured mypy pass.
The full suite at the preceding split checkpoint passed 2,092 tests in 150.18 seconds;
this does NOT qualify subsequent preset changes or the complete remaining release.
D07/D08 reviewed replacement, D10/D11, F01 and broad release qualification remain pending.

## Mesh replacement headless foundation (desktop integration pending)

D07 shared operations now provide scp.mesh.replace.assess/status/apply/cancel. Assessment
imports/evaluates owned native geometry and captures proposed bindings in a read-only
coordinator job. It does not change document/history. One owned candidate is retained.
A native canonical polygon/index correspondence check distinguishes safe indexed reuse
from lost correspondence; matching vertex counts alone are insufficient. Existing import
units/up-axis defaults are reused. Lost indexed bindings/weights and required rebindings
are listed with stable approval keys. Apply requires all listed approvals, rejects stale
read sets/authored definitions/incoming relationships, installs the complete record set
atomically and propagates through existing lifecycle/dependency mechanisms.

Reviewed SCP child recapture preserves pose within floating-point tolerance; Anchor and
Fiber recapture use shared confirmed placement. Fiber captures mark pins for rebinding
while temporarily constraining capture to existing targets, restoring authored scope
preferences afterward. Captured records publish as a complete batch instead of entering
ordinary point-edit preparation again (which would retain obsolete material references).
Shared controls survive removal of incompatible indexed bindings. One undo restores source.

Six mesh integration cases plus architecture/preset tests (13 total) pass. Native build
and all five native tests pass; Ruff and configured mypy pass. Desktop chooser/review,
additional field/branch/tissue-region/lifecycle evidence and broad qualification remain
pending; this is an intermediate API checkpoint, not a completed D07 workflow/release.

## Mesh replacement desktop checkpoint

D07 now has Replace source mesh in the Primitive inspector, native file selection and a
searchable/virtualized approval list with affected names. Assessment remains background
read-only work. No-effect/safe replacements apply directly as one undo action; a review
opens only for required rebind/discard actions. Main owns the file dialog so it opens
from a hidden review; both dialogs participate in the shared modal keyboard guard.

The GUI adapter caches status by session/token/state/document revision and does no idle
polling or model work when inactive. Metadata edits and newly incoming references now
mark the assessment stale as well as numerical read changes. Removed records can still
be described from the retained assessment baseline. Profiler ownership includes native
resources retained by the replacement candidate. Complete prepared object/entity batches
publish together, preserving junction consistency and avoiding ordinary edit recapture.

Ten mesh integration tests plus architecture pass (12 total): previous cases plus source
unit/up-axis preservation, failed/canceled assessment without authored edits, metadata/new
relationship staleness and non-root owner pose preservation. The offscreen actual inspector
button/file dialog/review/select-all/apply workflow passes, including automatic subsequent
safe replacement and one-action undo. Construction and preset offscreen checks also pass.
Broader branch/region/96-muscle assembly, performance, native style/full gate and packaging
qualification remain. D08/D10/D11 and F01 are still outstanding; no release/main merge.

## Tissue retarget and common replacement checkpoint

D08 now supports tissue.source.options and tissue.source.replace.assess/status/apply/cancel,
plus Change construction source, searchable virtualized attached-construction selection,
shared review and direct safe application. Cross-family evaluator/smoothing/relaxation/
crop/side/stacking changes are listed explicitly. Compatible fields/regions are preserved;
incompatible material fields/masks and selected stacking regions require explicit discard
approval. Target-relative region goals and incoming bindings use shared confirmed capture.
Sources remain shared live objects; old sources are preserved. Missing surface roles fail
actionably rather than substituting Final for Base (covered by a regression test).

Worker evaluation reuses the native base/rest/intrinsic/plan/final pipeline and material
publication records. Complete accepted bundles mark/schedule consumers while excluding
already prepared outputs; tests assert no redundant own-stage jobs after application.
Common candidate ownership, snapshot/registry-membership checks, approval validation,
record publication and the desktop review lifecycle now serve both replacement types.
Metadata/new incoming references/object creation/deletion stale the candidate. Mesh import
and tissue capabilities remain separate producer policies; no new worker pool was added.

A Manual-source case exposed false dependency edges: fixed-parent Fiber edits declared
unused tissue candidates that capture never reads. Support selection is now owned in core
and shared by capture and dependency declaration. Actual Any-parent searches still declare
all candidates. The Manual retarget/provenance case and Any-parent read-set regression pass.

Qt qualification found an access violation while a subclass property used an inherited
notify signal. A dedicated choicesChanged signal fixed it; complete engine/source-picker
and mesh replacement acceptance pass. No exception suppression or visible desktop input.

Twenty-six focused retarget/support/replacement/architecture tests pass, with Ruff and
configured mypy. Cases include Surface/Point/Curve changes, incoming Final bindings,
rejected unavailable Base role, field preservation/discard review, package roundtrip,
Manual accepted provenance, undo and no duplicate own-stage calculations. Extended mesh
and tissue retarget offscreen acceptance pass. Broader branches/crops/stacking assemblies,
full gate/profiling/packaging remain pending. D10/D11 and F01 remain outstanding.

## Quick Fiber creation checkpoint

D10 now has a dedicated Place Fiber toolbar action and shared fiber.place operation.
Every provisional click uses displayed native surface picking; misses add no point.
First click starts, Shift-click continues, and plain click from the second point finishes.
Backspace removes a point; Escape/cancel leaves no authored object. Generic keyboard
modifier routing is reused. The accepted Fiber is selected after background publication.

An owned provisional polyline exists only inside the worker snapshot. Existing confirmed
attachment capture binds every clicked point to its explicit target. Existing native
routing solves the first path before complete publication; no straight placeholder is
published as accepted ROUTED geometry. The normal authored-job transaction, revision
proof/retry and history replay remain shared with curve-to-Fiber creation. A dedicated
creation scheduling policy composes capture and routing estimates in the same coordinator.

Headless tests cover an obstacle-avoiding initial route, explicit target preservation even
with coincident candidate surfaces, atomic validation, cancellation, undo/redo and no orphan.
Desktop tests cover misses, hover, continued placement, Backspace, cancellation and accepted
selection. Twelve focused tests including existing Fiber creation and architecture pass;
Ruff/configured mypy and actual offscreen QML toolbar/creation/undo acceptance pass.
No interactive viewport geometry claim is made. Full suite at the preceding checkpoint:
2118 passed in 153.49 seconds. D11, F01 decision and broad qualification remain pending.

## World-space Fiber display checkpoint

D11 now has per-workspace fiber.presentation/inspect, persisted finite nonnegative radius,
and an inspector numeric control. Default radius is .001 metres; zero retains centerline
presentation. Numerical paths, collision clearance, attachments and anatomical undo remain
unchanged. Fibers remain independently styled in different workspaces.

Native af_path_display_tube transforms accepted centerline samples first, then constructs
constant-world-radius rings, caps, canonical faces, render chunks, bounds and picking tree.
The desktop uses read-only jobs in the existing coordinator with a dedicated cost policy,
retained paths and cancellation. Each visible Fiber retains only its latest accepted tube;
current/staged meshes remain leased through RenderModel and appear in profiler ownership.
Positive-radius replacements retain complete current geometry until frame publication;
exact picking queries that displayed mesh rather than a centerline with pixel width.

Ten focused geometry/presentation/display/architecture tests pass: uniform, nonuniform and
reflected transforms, bounds, closed seams, schema roundtrip, no numerical invalidation,
no authored undo changes, retained display, matching frame-boundary picking, superseding
edits and resource release. Existing 22 quick/Fiber interaction/creation cases also pass.
Native build/all five tests, Ruff/configured mypy and targeted native style pass.

Texture-only QQuickRenderControl acceptance now renders actual native tubes with no visible
window. The Qt offscreen platform plugin cannot initialize D3D11 here; the normal Windows
platform plus texture-only render control works without showing or controlling a window.
Inspected radius .005/.04 m captures measure 5/33 pixels and exact picking passes. This is
actual offscreen rendering evidence, not interactive acceptance or assembly performance.
The new Fiber scene must be a View3D sibling; nesting it below an empty PathScene repeater
made it absent from the scene and was corrected before this checkpoint.

Full development gate, representative assembly/performance qualification, packaging and
F01 user decision remain pending. No release version advance or main merge.

## Integrated gate and production display qualification

The full development gate passed at cc15855: Ruff/format, configured mypy, native build,
all five native tests, full native style, PowerShell checks, 2131 pytest cases in 154.91s,
numerical dependencies and native doctor. Subsequent native-registration/test/docs changes
have targeted checks passing; a new complete pytest run is in progress.

Offscreen replacement, tissue retarget, SCP split, construction editor and preset tools
all pass without warning suppression. Actual texture-only radius rendering remains qualified
separately from modal/controller tests; no foreground desktop or mouse/keyboard takeover.

The corrected local 96-muscle assembly contains 59 SCPs, 326 Fibers, 96 Membranes and 96
Tissues. All 326 read-only display jobs succeeded; source geometry/path buffers hash exactly
before/after, and the entire document/attachment records and undo position remain unchanged.
The profiling report is complete with no losses and zero unattributed native bytes. It
captures 326 tube calls, averaging 1.31ms and max 8.11ms in this run. Whole first projection/
submission was 342ms, coordinator work 694ms and CPU-only staging-loop total 58ms. These are
single-run costs under background validation, not speedup, GPU, frame-rate or input-latency
claims. Collector cost is recorded separately and is not subtracted from application time.

The first report exposed an attribution gap: 326 successful jobs but only one native tube
span, and the library ended with a raw ctypes function. New display signatures had been
registered lazily during concurrent work. Moving registration into the existing native
engine initialization restored all 326 native spans. The maintained production qualifier
now requires job/call-count agreement and report completeness; a repeated-worker regression
also checks full attribution. No profiler event-loss mechanism or numerical kernel changed.

Local evidence: build/parity-workflows-034/fiber-display/assembly-registered/display.afprofile.zip
and qualification.json, plus the inspected radius captures. The reusable qualifier is
tools/fiber_display_qualification.py; it opens a copy read-only and writes no source project.
F01 remains pending; no final corrected assembly, release build or main merge is claimed.

## Final independent qualification and ownership review

Latest full pytest: 2136 passed in 155.36s. The prior complete development gate includes
full native style, all five native tests, dependencies and doctor; no native source has
changed since that gate. Current Ruff/format/mypy and focused display/architecture checks
pass. A final change makes dispatch capture explicitly use the owned document snapshot;
its focused checks pass after the aggregate suite. No interactive acceptance is claimed.

Additional regressions cover initial routing failure without a straight/orphan publication,
bound quick-Fiber endpoints after parent motion, and an actual geometric child retained
on the first split SCP through shared-Hook movement. A queued display whose Fiber disappears
is discarded as obsolete at capture/publication, preserving old display and avoiding a
missing-resource failure. Prepared resources remain owned until the coordinator retires work.

Final texture-only rendering again passes 5/33 pixel radius checks. The final production
report under build/parity-workflows-034/fiber-display/final-qualification is complete,
contains all 326 native calls and passes unchanged source-buffer/document/attachment/undo
assertions. Measured first projection/submission 345ms, work 737ms, CPU staging total 57ms;
these single-run observations are not controlled speedup or physical frame-latency evidence.

Coordinator-authored ownership review: numerical geometry stays native; application
operations own policies/transactions and replacement candidates; the desktop owns display
intent and staged leases. Quick creation reuses authored publication. Both replacement
families share lifecycle/approval/read proofs while retaining separate compatibility
policies. There is one task coordinator and no additional worker pool. Display resources
cannot become anatomical providers or mutate accepted numerical paths. Remaining end-to-end
acceptance is the F01 decision/correction, final assembly and canonical release packaging.
