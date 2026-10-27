# Skin migration 0.4.0

- Task branch: `codex/skin-040`; integration: `main`.
- Starting revision: `6260864` (qualified 0.3.7 UI workbench).
- Status: envelope and topology pipelines connected; full skin workflow remains in progress,
  not merge-ready. Schema 7, immutable resources, shared commands and vertical inspector exist.
  Durable deformation, shortcut fitting, OBJ export and release qualification remain unfinished.
- Last updated: 2026-10-27, Europe/Bucharest.
- Direct work, no subagents. All execution/validation must remain background/hidden.

## Outcome and acceptance

### Resumed implementation: approved corrections, 2026-10-26

User authorizes replacing the approximate proxy collapse and half-mesh clipping with
the required pinned Blender 5.0.1 Decimate/BMesh implementation subset. Preserve actual
topology mutation, ordering, tolerances and outputs; do not silently sanitize source
degeneracies or substitute another algorithm. Verify against addon fixtures and actual
anatomy before continuing the remaining 0.4.0 workflow.

Accepted departures remain: instance-aware density ownership/deterministic ties;
accepted material-chart guidance and compatible surface tissues;
native spatial queries and local triangle predicates (remaining parity limits still need
qualification). These are the user's accepted items 3–6, not full geometry acceptance.

Revise external execution policy: ordinary work has no arbitrary elapsed-time or 4 GiB
hard limit. Bounded retained logs must not terminate computation. Preserve cancellation,
process ownership and genuine failure reporting. Use resource-aware admission/concurrency;
retain the addon's four-thread tetrahedral setting rather than forcing one thread.

**Approach changes require discussion first.** If this agreed implementation approach
needs replacement or a further algorithm change, stop implementation, explain the
observed blocker and proposed alternative, and wait for the user's decision. This
overrides general autonomous approach-replacement guidance for this work.

Current recovery: execution/admission corrections are in f0bb41d/a6977e1; pinned BMesh
integration and anatomical qualification are in ab3aa7b/be63292. The source-normal
boundary and fixtures are committed. The user resolved the centerline weighting question
by restoring thin Fiber surfaces on October 27; current qualification is recorded below.
Root __init__.py is unrelated. No 0.4.0 release/main merge.

Execution correction: no default process time/memory cutoff; bounded diagnostic tail
instead of terminating on log volume; process-tree termination handle race fixed;
tetrahedral thread setting restored to four. Fourteen focused backend/proxy tests pass.
Resource-aware admission is recorded below. The maintained Blender 5.0.1 geometry-only
BMesh subset is now integrated in the C++17 library, replacing approximate Decimate and
half-cutting. Source hashes and omitted unreachable definitions are recorded in its manifest.
Five canonical Mesh.from_pydata Decimate controls match exact coordinates/connectivity;
symmetry comparisons retain source cut degeneracies. Twenty-eight focused parity, ownership,
density and provenance tests pass. Source edge order is retained through smoothing and
deformation. Native build succeeds in the C: tree. Broader anatomy, style, lifecycle and
release acceptance remain pending; do not infer them from the compact fixtures.
Original extraction/probe remain under ignored build/skin-040; no WIP artifacts were added.

Resource admission now belongs to the existing coordinator. Immutable per-task estimates
reserve CPU/memory for concurrent workers; estimates are reassessed before dispatch capture.
Externally parallel remeshers reserve available CPUs without changing backend settings.
Large work may run alone even when its estimate exceeds capacity. Waiting remains cancellable;
bounded inline edits remain available. Forty scheduler/lifecycle/architecture tests pass,
configured mypy passes 493 files, all five native CTests pass. Broad regression is recorded below.
No reference/deformation/fitting/export acceptance is implied by this checkpoint.

Anatomical preparation qualification found/fixed a missing conversion boundary:
Blender's Decimate uses regular Mesh vertex normals, not recalculated BMesh normals.
An isolated captured-normal experiment identified this cause; the native adapter now
ports Mesh's Newell/angle-weighted normal calculation. Skull (428,230 triangles) and
torso (4,481,616 triangles) both match exact positions/connectivity after all three
stages: collapse to 64,000 faces, ten smoothing iterations, BMesh half cut. Source
captures are unchanged. A 2,048-triangle skull region catches the former mismatch.
Evidence and paired renders: build/skin-040/bmesh-anatomy/. Both skull and torso renders
inspected. No algorithm replacement was introduced. First broad run: 2,485 passed,
two failures. Corrected the renderer test to patch the shared launcher owner. The inline
attachment timing test passed alone, in 30 serial repeats and in the full rerun; its
original intermittent cause is not established, and failure diagnostics were added.
Final full rerun: **2,487 passed**, 3,199 existing Qt deprecation warnings, 356.51 seconds.
Ruff/format, mypy (493 files), native CTests (5/5), changed native-file style, dependency
imports and lock checks pass. Complete portable/interactive release acceptance remains open.

Resolved next-stage decision: the unmodified addon deformation sampler requires surface
faces and positive area. A three-point centerline produces `Invalid reference connectivity`;
the native area routine returns all-zero weights. A triangle using those points succeeds
with area 0.5. Evidence: build/skin-040/centerline-reference.json, including source hash.
The user chose to restore the addon's small-thickness surface approach, superseding
centerline-only capture. The proposed envelope-area weighting experiment was not
implemented and is not the chosen approach. Deformation sampling stays area-based.
Retained the previously written production-envelope, topology-button and hidden-GPU
acceptance tools after ownership/static review. Their complete runtime qualification
against this corrected branch remains pending; do not infer it from their presence.

### Thin Fiber restoration, October 27

Native capture now builds a Blender-compatible POLY bevel from accepted Fiber paths:
12-vertex rings, minimum-twist frames, source duplicate handling and uncapped open ends.
The four unchanged upstream frame functions and required BLI math are pinned by hashes;
the adapter owns arrays, cancellation and publication. Skin radius defaults to 1 mm,
is edited in the Skin contributor panel, persists with coherent undo, and does not use
workspace display thickness. Source/mirror pairs share the source tube resource.

Six Blender controls (straight, bent, closed, duplicate-point and reversal cases) match
coordinates within 1e-8 metres and exact quad/triangle order. Focused settings, mirror,
persistence and native checks pass; final static/UI/broader evidence follows below.
The first four-Fiber-only envelope timing was withdrawn after visual inspection: without
supporting SCPs the output has boundary planes and is not representative skin. The full-
skeleton attempt also failed under the benchmark's default 1 GiB assembly budget; it is
not a completed timing or a production-policy change. Corrected trials use the production
worker budget and four forearm Fibers with their three actual attachment SCPs. Capture-only
stress with all 326 accepted Fibers takes about 422 ms and 27.5 MB of captured arrays
(not total resident memory). Consumed Fibers remain
suppressed in production. Separate profiler captures and raw trials are under ignored
build/skin-040/fiber-thickness-production (the invalid envelope benchmark is retained as
rejected evidence). The addon sampler accepts all six fixtures, with identical selected
indices, five exact area matches and a 1.2e-7 relative closed-loop difference. Offscreen
radius editing/undo passes. The first broad run passed 2,499 tests and caught two topology
guide regressions: those callers still expected path handles from the now-mesh capture.
Separated accepted path capture from physical surfaces for loops and FLOW; focused tests
now pass, including radius-independent FLOW. The final full rerun passes **2,502 tests**
(3,199 existing Qt deprecation warnings, 268.94 seconds).

Corrected performance evidence: `build/skin-040/fiber-thickness-forearm/` contains raw
trials, NPZ output, paired render, addon precision check and a separate `.afprofile.zip`.
Three serial counterbalanced profiler-off trials per mode, grid resolution 220, no unit
rescaling: capture/fields/scene/envelope total median 3.380 s centerlines (3.347–3.463)
versus 105.773 s tubes (105.545–107.003). The four tubes themselves take 3–4 ms to build/
capture. Skin triangles rise from 64,006 to 1,585,630. The unmodified addon exterior-gap
preflight requests a 4.911× finer lattice: coarse voxel 0.0471715, gap width 0.0528283,
fine voxel 0.00960515 in this project's stored metre coordinates, 564 qualifying faces.
This confirms inherited gap preservation can dominate the small tube-generation cost;
no refinement rule, tolerance, gap policy or radius was automatically changed. Paired
envelopes were visually inspected. This benchmark intentionally omits consuming tissues:
the saved production assembly has 96 accepted tissues covering all 326 Fibers, so none
are bare contributors there. Do not extrapolate the benchmark to full-assembly latency.
Timing includes no UI/publication/reference solve; background machine load was not
controlled. Separate profiled trials are not used for the medians. The initial profiler
capture exceeded its default 120-second window and evicted the long span. A completed
repeat uses the existing configurable 600-second window, retains both envelope calls and
reports **zero truncated events**. The default application recording window is unchanged.
Ruff/format, mypy (494 files), 5/5 CTests and offscreen metre/mm radius controls pass.
The matched-build hidden GPU check passes at diagnostic resolution 64; actual source,
envelope and isolated images were inspected. The fixture's original grid-24 run fails
with `Unresolved gap precision`; the **unmodified addon reproduces the exact same error**
on these inputs, including source triangle IDs and clearance. Production-resolution 220
could not run this cube fixture under the available-memory budget (~1.5 GB RAM free,
~540 MB worker allocation). Neither failure was bypassed through a production change.
Logs: `build/skin-040/fiber-hidden-gpu{,-addon,-production,-matched}.log` and addon JSON.
The source grid-24 error remains a known algorithm limitation, not a thin-bevel parity defect.

Validation setup correction: a numerical DLL override alone does not redirect the Qt
viewport's build directory. Loading C: numerical and E: viewport DLLs produced empty
geometry with apparently active model rows. Rerunning with both using the C: build
renders the actual geometry. The maintained scene check now waits for displayed assets
and asserts a visible fixture pixel; a log saying it rendered is insufficient evidence.
For this temporary build, set `runtime.build_directory` to the C: build **before importing**
`skin_scene_acceptance`, alongside the numerical-library override. No physical desktop
interaction or complete packaged-release acceptance is claimed.
This is an incomplete 0.4.0 checkpoint; no release/version bump/main merge is authorized
by these partial checks. Historical centerline notes below describe superseded checkpoints.

### VCP context follow-up, October 27 — no algorithm changes

User requested the comparison with related VCPs included. Read accepted definitions and
only the required mesh assets directly from the unchanged 96-muscle project; no source
recalculation, edits, resaving or workspace-dependent contributor selection. The focused
case contains the same Humerus/Radius/Index SCPs plus Flexor carpi radialis.L and Pronator
teres.L. These two accepted VCPs represent five Fibers, including all four from the earlier
bare-Fiber experiment. Shared contributor policy excludes all five: **zero bare Fibers**.
Centerline/tube choice therefore makes no difference to this case's skin inputs.

The focused envelope attempt did **not** complete. Its 1,741 source vertices / 3,328
triangles reached `Skin mesh assembly exceeds worker memory budget`; only ~1.04 GB RAM
was available at capture. A separate original-addon precision check at the corresponding
~365 MB budget chooses coarse resolution 160 (target 220), voxel 0.0648608, and detects
214 gap faces with minimum protected width 0.00504122 m. Its requested fine voxel is
0.000916585 m, a 70.7635x linear refinement. This is not a completed runtime comparison
or evidence that final VCP skin looks better/worse. No partial mesh was presented as skin.

A wider inventory includes all 28 accepted VCPs whose source bindings touch those three
SCPs, plus their other supports: 14 SCPs total, 103 represented Fibers, zero bare Fibers,
41,055 input vertices / 77,676 triangles. Accepted anatomy was rendered and inspected.
Its source-addon preflight asks for 100.229x linear refinement (coarse 0.0981261 m,
fine 0.000979017 m, 1,054 qualifying gap faces). The larger full envelope was not run
after the focused failure. Do not claim a VCP envelope or extrapolate timings from it.

Evidence lives under `build/skin-040/fiber-thickness-tissues/{paired,related}`: accepted
input arrays, identity/coverage/hash reports, source preflight values and fixed-camera
`anatomy-inputs.png` previews explicitly labelled **inputs, not completed skin**. Scripts
`build/skin-040/check_tissue_context.py`, `check_tissue_precision.py`, and
`render-tissue-context.py` reproduce this read-only experiment; all functions <=15 lines.
The input hash for the focused case is
`7545889f6bbd0ce344d0c60b23ae5b9f381cc7017171ea186e0b9f57f4a0936f`.

**Correction after the user's challenge:** the fine-grid measurements are valid, but the
assembly failure was triggered by an extra standalone-only estimate cutoff, not by a
demonstrated addon failure or genuine OS allocation failure. The prior explanation
incorrectly conflated these. Do not use this failed test to claim the addon cannot build
the same scene. Gap refinement alone does not explain the policy discrepancy below.

### Assembly execution-policy correction — qualification in progress

Code inspection found the port subtracts coarse fields and tile storage from a single
budget, then applies an additional 256-byte/vertex + 192-byte/triangle assembly estimate
as a hard rejection. The addon passes its current working budget to sparse field storage
and imposes no equivalent mesh-assembly ceiling. This is a missed part of the already
approved execution-policy correction, not an authorized numerical departure.

A discriminating experiment gives both implementations identical cube geometry/fields
and an 8 MiB field budget: original addon succeeds with 11,703 vertices / 23,180 triangles;
the prior standalone fails with the same assembly error as the tissue case. After removing
the extra aggregate/assembly rejection, standalone also succeeds. Original field cache
limits, cancellation, source geometry algorithms and allocation-error reporting remain.
Application code now refreshes available field working memory at the reconstruction stage,
matching the source lifecycle rather than passing a stale preparation estimate.

Evidence: `build/skin-040/assembly-budget-parity{,-after}.log`; new focused regression
requires identical output under the 8 MiB field budget. Native build passes; focused,
broader, source-geometry parity and actual tissue-case reruns are still pending. This does
not establish the full forearm result yet. No additional algorithm changes are authorized.

User requests moving existing addon skin functionality into the standalone app for
0.4.0, including calculating fitted bones/weights to reproduce shortcuts. Preserve
anatomy, geometry/attachment behavior and the existing engineering,
checkpoint/push and single-distribution rules. Package version remains 0.3.7 during implementation.

## Decisions and relevant files

- [Specification](../specification_040.md) and [implementation plan](../implementation_040.md)
  are confirmed. Schema 7 retains readers 4–6; stale export offers explicit accepted/update/cancel.

- [Migration inventory](../skin_040_inventory.md) records production code owners,
  settings, current-versus-legacy behavior, numerical porting work and future evidence.
- Addon source `fae36aba1b208676cf21d7c4a78a20d5b1f68c66`; inspected skin paths clean.
- Full current skin pipeline plus shortcut-to-bone fitting is in scope.
- Confirmed delivery priority: reproduce existing addon behavior first, then improve it
  in later work. Preserve algorithms/defaults/supported cases while adapting ownership
  to the standalone architecture; keep proposed enhancements separate from migration.
- Export starts with OBJ, preserving quads; keep a narrow, extensible format interface.
  OBJ does not serialize rigs. Retain fitted data/preview in the project.
- Add Skin to the existing right inspector and arrange Shape / Shortcuts / Inspect /
  Skin vertically on its left edge. This replaces the proposed separate Skin mode.
- Reuse the coordinator, native geometry/material contracts, brushes, Issues, profiler,
  immutable results and workbench; no Blender runtime or duplicate scheduling system.
- Current addon publishes usable quality-warning geometry. Older hard-rejection prose
  is superseded by actual `core/mesh_issues.py` and its callers.
- Bone fitting is untracked local addon work; its source fingerprints and actual public
  versus authoring-only contracts are recorded in the inventory. Do not attribute it to
  the clean source commit or claim existing qualification of its standalone port.

## Current state and verification

Read panels/operators, model/settings, field/gap kernels, topology/guide preparation,
reference/LE/FAST/contact code, bone sampling/fitting/preview/publication and existing
fixture/test names. Checked official
upstream APIs. No runtime/parity/GUI qualification or geometry acceptance performed.
Initial source qualification: six addon bone-fitting tests and 21 deformation tests
pass under the standalone Python 3.12 environment using the existing addon native DLLs.
These establish source controls only, not rebuilt-native or application parity. Matching
`pytetwild==0.4.2` and `pyinstantmeshes==1.0.0` import in this environment.
Source controls also pass 35 skin/gap/tile and 40 topology tests. These use addon binaries,
not a rebuilt standalone skin kernel. Source DLLs/projects were not modified.
Foundation contracts: 17 targeted tests passed. First broad run: 2,256 passed and one
expected-version test failed because it still rejected newly supported schema 7; corrected
its unsupported version to 8. Broad rerun: 2,258 passed. Ruff/mypy and function limits passed
for foundations. Offscreen skin tab navigation, decimal setting and Undo checks pass;
font-enabled capture inspected at `build/skin-040/ui/skin-settings.png`.
Native coarse fields now build in the existing library: raster, Euclidean distances,
26-connected exterior, quantized collagen and combined envelope. Twelve comparisons
against unmodified addon modules at resolutions 16/32/48 agree within roundoff (1e-12 gate).
Seven initial native-adapter/architecture tests passed; native CTests 5/5.
Local parity detail: `build/skin-040/field-parity.json`; rerun with
`tools/check_skin_fields.py <addon-root>`. Full settings and remaining pipelines still pending.
Gap kernels are pinned with hashes under `native/migration/skin` and compile privately
without OpenMP. Owned gap-scene sampling passes source gap-policy/winding/same-owner cases.
MC33 C++ extraction is qualified against scikit-image 0.25.2: 6,344 initial cases exact
in vertices and faces, including binary/ternary cubes and 33-cubed random tiles. Source
subset pinned with both licenses under `native/vendor/bioimage-cpp`. Current native and
adapter checks at that checkpoint: five CTests and 17 focused Python tests passed.
Native reconstruction now connects the field and gap kernels through protected-grid
preparation, bounded tiled extraction, native stitching, support filtering and eight
constrained Taubin iterations. Cube, separated-cubes and overlapping-cubes source controls
match vertices/connectivity exactly. `build/skin-040/envelope-review.png` visually inspected:
coarse-fixture protrusions occur in both addon and port, so parity is not shape acceptance.
Running cancellation inside native tile preparation passes and does not poison reuse.
The five-finger source-control experiment was stopped after more than 45 CPU-minutes
inside the addon, before reaching the standalone phase. No performance/geometry result
exists for that fixture. Log: `build/skin-040-digits-parity.log`. Do not restart blindly:
add progress/timeout diagnostics first. Its invocation was
`check_skin_envelope.py <addon> <digits_blend.capture.npz> Thumb,Index,Middle,Ring,Little build/skin-040/digits`.
Native material binding capture is connected through the source scene. Typed SkinStage
records own stage-buffer resources; save/read retain them and reject checksum corruption.
Fourteen binding/foundation/architecture tests passed at the binding checkpoint.
Native diagnostic bundles now retain quality, gap coverage, source intersections and
removed-component counts. Named decoding distinguishes unavailable checks from clean
findings. Eight envelope/architecture tests pass; mypy (442 files), Ruff and format pass.
The three source controls also match all six binding arrays exactly, including retained
source/triangle identities, barycentrics, weights, offsets and support. Contributor capture,
coordinator/publication and complete UI remain pending. No production skin acceptance.
Next integrated checkpoint: batched C++ contributor transforms/assembly, reflected winding,
source indices and absolute gap distances; source-selection policy suppresses fibers represented
by accepted tissue without consulting viewport visibility. Sixteen foundation/capture tests
passed. Instant Meshes file API produces 246 actual quads on the dependency cube; its array
API silently triangulates on readback and is not suitable here. PyTetWild produces 2,844 tets
with one thread. These are executable dependency probes, not anatomical qualification.

Envelope build now has a shared command (`skin.envelope.build`), native worker task, dispatch
observations, owned binding/source arrays, coherent undo, and persistence. Three integrated
job tests pass at resolution 24; production default remains 220. The latest broad run before
this job integration passed 2,286 tests (175 seconds). Topology, final deformation, fitting,
OBJ, generation viewport display and complete Issues integration remain unfinished.

Skin settings UI now includes symmetry plane, proxy resolution, constraint strength and FAST
handles. Offscreen decimal/integer edits, vertical navigation and Undo pass.
The user answered the bare-fiber question: **centerlines only**. The temporary 1 mm
skin-radius assumption is superseded and removed. Native field, gap-support and binding
work now accepts explicit segments; triangle sources keep their existing numerical path.
Centerline capture and binding checks pass, including a centerline-only envelope. Full
production anatomy, topology/deformation and release qualification remain unfinished.
App version remains 0.3.7; writer now schema 7 with readers 4–7. Unrelated root
`__init__.py` is preserved. Source `.blend` files remain untouched.

## Next actions

1. Finish envelope contributor/painting controls and production-anatomy qualification. Centerline-specific coverage evidence remains distinct from triangle checks.
2. Integrate qualified topology/tetrahedral dependencies and maintained native numerical preparation.
3. Deliver durable reference/deformation, shortcut fitting and OBJ through shared API and desktop.
4. Complete full lifecycle, profiler, geometry and portable-release qualification per plan.

All three initial questions are answered. No automatic minimal-bone search or
multi-shortcut rig composition is implied: preserve the existing configurable bone
budget and independent fits. General animation editing and rig-capable export remain
separate. No automatic remeshing on deformation and no silent backend fallback.

## Recovery inputs

Addon root is recorded in the inventory. Windows-only fixtures remain under
`E:/development/WIP_models`; local presence is not proof of geometry acceptance.
The containing Git commit identifies this checkpoint; inspect remote reachability
before resuming from another machine.

### Centerline checkpoint

Forty focused skin/capture/lifecycle/architecture tests pass. Native build and five CTests
pass; selected native style checks, Ruff and mypy pass. Cube addon comparison remains
exact (11,703 vertices / 23,180 triangles; all six legacy binding arrays equal). Offscreen
settings/navigation checks pass. Current broad suite is running in
`build/skin-040-current-tests.log`; do not claim its result until it completes.
Skin stage display was connected through existing staged scene rows with per-workspace
AUTO/Envelope/Topology/Final/Hidden selection; actual envelope viewport rendering still
needs qualification. Centerline binding kinds are explicit; line-specific coverage and
intersection diagnostics need separate evidence rather than inheriting triangle results.

### Envelope presentation and diagnostic checkpoint

The first full regression run found one profiler attribution regression from the earlier
provisional tube adapter (2,297 other tests passed). Removed that now-unneeded adapter
and restored the original display-only native boundary; the targeted profiler test and
12 related tests now pass. A fresh broad run is in progress in the same current-tests log.
Skin Issues now consume already-measured stage diagnostics, preserve accepted geometry,
and clear with Undo; the integrated test passes. Hidden GPU rendering of cube + bare
Fiber succeeds, with source/envelope/isolated captures under `build/skin-040/ui`.
The low-resolution envelope visibly retains the known coarse source-control protrusions
and open regions; these are reported and are not production anatomical acceptance.
Offscreen UI display/hide and settings checks pass. Workspace display edits intentionally
do not use document Undo; the initial display test was corrected to restore its workspace
setting explicitly. Full topology/reference/deformation/fitting/export work remains open.

Final check for this checkpoint: the broad rerun passes **2,299 tests** (183.95 s).
A closed/reflected-centerline capture test added after that run's collection also passes
in the focused suite. Ruff/format, mypy, native build/five CTests and selected native style
checks pass. Cube, separated-cube and overlapping-cube addon controls remain exact in
geometry/connectivity and all six original binding arrays. Hidden GPU and offscreen UI
checks pass with the evidence limits above. No release version bump or main merge.

### Contributor controls and collagen authoring

Added selected-source gap overrides and SCP Auto/Uniform/Painted collagen controls,
plus shared `skin.collagen.set`, `.fill`, and `.clear` operations. Clear follows the
addon by removing the map and choosing Uniform. Filled/all-zero maps are authoritative.
The common material-domain fingerprint was extracted from tissue field handling;
collagen capture now detects changed connectivity even when vertex count is unchanged,
then retains the documented uniform fallback and warning. Ten focused application,
desktop-projection and architecture tests pass; mypy passes (452 files). Offscreen
numeric edit, Fill and Undo passed and the contributor panel capture was inspected.
Brush strokes, remaining contributor topology controls and subsequent skin stages
are still pending. No new broad-suite or release qualification is claimed here.

### Collagen brush checkpoint

Collagen painting now shares the native brush, query scheduler and desktop gesture
lifecycle with tissue weights. Domain policies choose validation/capture/commit; there
is no second worker pool or Python numerical brush. Read-only previews retain displayed
geometry, use visible-only or Paint Through, and commit one topology-qualified edit.
Focused API/desktop tests cover cancellation, stale field rejection, undo and colors.
Offscreen controls and hidden GPU heat rendering pass; images were inspected. Mypy
passes 454 files. Full anatomy and the remaining topology/reference/fitting/export
stages are still pending; this is not 0.4.0 release qualification.

### Topology preparation checkpoint

The broad post-brush regression run passes 2,313 tests (178.45 seconds). Added
subtree-budget/FLOW contributor controls and nearest-explicit-ancestor budget warnings;
offscreen controls pass after correcting tuple-to-QML list conversion. The native
FLOW cross-field kernel is now namespaced behind owned mesh inputs and cooperative
cancellation, with source fingerprint retained. Four direct addon-DLL field controls
match exactly (maximum error zero). Three native-adapter tests cover guidance, no
guidance, invalid samples and cancellation; seven focused tests including budgets and
architecture pass. Native rebuild and five CTests pass; selected clang-tidy emits only
suppressed header warnings. Full topology generation and anatomical acceptance remain
pending. Next: integrate feature paths, capture/assembly and backend execution.

### FLOW guide recovery checkpoint

Native feature routing matches the addon DLL on the compact control. Accepted tissue
charts and explicit Fiber paths now have owned native guide capture, including reflected
frames. Capture uses accepted material kind during pending edits, not the new authored
kind. Fourteen focused tests pass; configured mypy passes 458 files, Ruff/format pass,
and native guide clang-tidy reports only suppressed header warnings. The two-row branch
fixture correctly has no interior FLOW samples, matching the addon rejection; this is
not proof of successful branched anatomical capture. Four field controls still match
exactly. No generator integration, full topology acceptance or release qualification yet.
Next: external backend lifecycle, loop guides/density/assembly, then downstream stages.

### External process ownership checkpoint

Added a Windows native backend runner executed synchronously by the caller's worker.
Creation assigns the process to a memory-limited Job Object before execution, allows
only designated standard-stream handles to be inherited, hides windows, and terminates
children on return/cancellation. Tests exposed asynchronous cleanup; the runner now
waits for root termination and job accounting before returning. Eight process tests
cover timeout, cancellation, child cleanup, memory limits, log limits, exit status and
Unicode/quoted arguments. Architecture checks pass. Windows-only runner qualification
is explicit; no Linux fallback or additional worker pool.

Verified all 30 pinned addon QuadWild bundle files and copied them into ignored
`.tools/quadwild`. A real isolated cube trace exits 0; quantization returns the known
addon Windows code 2147483651 with parseable 26-vertex/24-quad output. Evidence/logs
are under `build/skin-040/backend-smoke`; this is process qualification, not complete
topology acceptance. The bundle still needs maintained setup/package integration.
The full regression is running in `build/skin-040-resume-regression.log`.

### Guided backend checkpoint

The broad regression before the final backend exchange changes passed 2,333 tests
(181.12 seconds). New focused process/guide/backend/architecture checks pass 27 tests;
Ruff and configured mypy pass (464 files). Native build/five CTests pass and selected
clang-tidy reports only suppressed header warnings. Do not conflate this evidence with
a new broad run after the latest changes.

Added pinned-bundle verification and `tools/setup_quadwild.py` (explicit setup only;
no runtime download), package-copy support, native feature-face mapping and native
quad-count calibration. The internal backend preserves four calibration attempts,
15% target tolerance, invalid-patch warnings and sparse-path retry with direction
constraints retained. Direct complete addon/standalone cube comparison produces
identical 98 vertices / 96 quads, zero maximum coordinate error, identical polygons.
Evidence: `build/skin-040/quadwild-parity/parity.json`. Both retain the target-count
limitation and known Windows abnormal-exit warning. No anatomical acceptance yet.

This remains internal integration, not a public topology-build command. Next work:
batch source guide assembly; loop patch preparation; density/proxy/symmetry and
refinement; coordinator publication and desktop controls; persistent reference and
LE/FAST; fitting/export; full geometry/GUI/package qualification. Version stays 0.3.7.

### Guide assembly and density checkpoint

Added native batched guide assembly: distinct source-local patch IDs become distinct
global FLOW regions, with retained `(source index, local region)` provenance and
combined path offsets. Capture assembles this data without changing accepted sources.
Cancellation, invalid buffers and empty inputs are tested.

Ported addon density initialization, lumped vertex areas, median fallback and eight
log-smoothing/budget-correction iterations to C++. Metadata budget plans preserve
nearest explicit ancestors and the document remainder. Direct addon comparison on
three 1,600-vertex controls has maximum length error below 2.7e-16; local native
runs were below 1 ms, which is kernel evidence, not application profiling.
Evidence: `build/skin-040/density-parity.json`. Sixteen focused tests pass; configured
mypy passes 467 files. Native build/five CTests pass, selected style checks have only
suppressed header warnings. Ownership assignment, proxy preparation, loop patches,
symmetry/refinement and coordinator publication remain pending. No release claim.

### Proxy smoothing and connected-guide checks

Accepted tissue guide capture now passes through the real QuadWild backend in a
focused integration test. Added native Blender midpoint proxy smoothing with four
Blender 5.0.1 fixtures; five smoothing tests plus the headless/architecture checks
pass. Inspected rendered parity at `build/skin-040/ui/proxy-parity.png`. Native build
and five CTests pass; selected clang-tidy reports only suppressed header warnings.

An initial broad run had one headless failure while Python/native ABI edits overlapped
the active test run (2,348 passed). Rebuilt the matching DLL, confirmed the affected
headless test passes, and started a fixed-snapshot full rerun in
`build/skin-040-proxy-regression.log`; read its completed result before claiming success.
Do not edit runtime bindings or rebuild the native DLL during an active broad run.

Remaining: ownership assignment, decimation, closed-loop patches, symmetry and
refinement, topology publication, persistent deformation, fitting/export and release.
Before porting ownership, inspect addon `_scp_trees`: dictionary keys use SCP identity
while captures can contain reflected instances; determine intended nearest-support
behavior with a mirrored fixture rather than silently carrying or changing that policy.

Ownership follow-up evidence: a compact addon diagnostic confirms reflected SCP
captures overwrite original-side samples in `_scp_trees`. For a tissue sample beside
original A at x=-2 (candidate bones A/B, B at x=-1), later mirrored captures at x=2/1
make the addon choose B. The diagnostic uses a tissue sample at (-2,0,0.01) and retains
all inputs in `build/skin-040/ownership-mirror-diagnostic.json`. This is an ownership
assignment defect, not an observed skin geometry failure. Preserve instance identity
when designing the port; qualify original/reflected candidate selection explicitly.

Final fixed-snapshot rerun: **2,354 tests pass** (266.80 seconds, 3,199 warnings)
in `build/skin-040-proxy-regression.log`. Ruff/format and configured mypy pass; native
build/five CTests and selected native style checks pass. This checkpoint does not
qualify complete 0.4.0 behavior, anatomy, desktop topology publication or packaging.

### Instance-aware topology ownership checkpoint

Added native source sampling, spatial indices, nearest-support attribution, tiny-island
cleanup, owner-to-budget mapping and nearest-vertex density transfer. Application capture
follows Fiber/Anchor bindings through Membranes and tissue chains, reusing mirror target
mapping and explicit midline sharing. Original/reflected samples remain separate while
budgets retain authored SCP identities. Centerlines contribute vertices/midpoints without
an invented radius. Missing supports retain explicit nearest-SCP fallback counts.

Sixteen focused ownership/density/architecture tests pass, including the observed mirrored
overwrite regression, indirect tissue anchoring, midline sharing, cancellation and invalid
source connectivity. Three direct addon controls (400/1,600/10,000 vertices) have identical
owner labels: `build/skin-040/ownership-parity.json`. Small-island ties are deterministic
(lowest owner ID), rather than depending on Python set/Counter iteration. Native build/five
CTests pass; selected clang-tidy has only suppressed header warnings. Ruff and configured
mypy pass (470 files). This is attribution evidence, not anatomical topology acceptance.

Next: connect density refinement, proxy decimation, loop patches/symmetry and complete
backend assembly to public coordinator/UI operations. Persistent deformation, fitting,
export and complete release qualification remain unfinished. No version bump or main merge.

### Conforming topology refinement checkpoint

Added owned native topology result bundles, all-quad split closure, adaptive candidate
selection, symmetric pairing, parity-safe budget search, proximity weighting and base
target calculation. Application density preparation applies proximity to accepted
surface-tissue sources before budget correction, preserving ordinary density otherwise.
Classification does not select the algorithm. No public topology build operation yet.

Direct addon comparison: all 64 small-grid split masks agree in geometry/connectivity
and parent labels; three adaptive budgets and one symmetry case agree; proximity
weights are exact. Evidence: `build/skin-040/refinement-parity.json`. Rendered and
inspected `build/skin-040/ui/refinement-parity.png`; this is a compact kernel fixture,
not anatomical acceptance. Twelve focused workflow/refinement/architecture tests pass;
configured mypy passes 473 files, native build/five CTests pass, selected native style
passes after splitting the boundary traversal helper. Broad regression is next.

Remaining topology: proxy decimation, loop guide patches, hole/transition assembly,
full symmetry/backend orchestration and public coordinator/UI integration. Persistent
reference/deformation, fitting, OBJ export and release qualification remain unfinished.

### Proxy collapse checkpoint (in progress)

The ownership/refinement full development gate passed: 2,371 tests, 3,199 warnings,
249.58 seconds; native checks and dependency import/doctor checks passed. Log:
`build/skin-040-ownership-refinement-gate.log`.

Qualified a narrow native proxy decimator using Blender 5.0.1 face-plane quadrics,
boundary weight 100, flat-region normal/edge cost, placement and face-flip rejection,
with existing libigl managing topology. This runs serially on the owning worker and
supports cancellation/memory limits. No Blender object/dependency runtime is included.
Generic QSlim was compared and not selected: it differs more from Blender on these
fixtures. The preserved source remains untouched; an unreachable target returns usable
geometry for an explicit count warning. Malformed/nonmanifold collapse inputs fail.

Six captured Blender controls include an open patch, sphere/ellipsoid and actual MC33
cube/gap/contact envelopes (6,574–40,252 triangles). The three envelope P95 distances
to Blender are below 2e-7 of source diagonal; curved symmetric meshes have different
collapse ordering, with maximum sphere discrepancy 0.00656 diagonal at 75% reduction.
This is not exact-connectivity parity. Rendered/inspected both fixture comparisons;
artifact folder: `build/skin-040/decimation`. Fourteen focused checks pass. Native build
and five CTests pass; selected style, Ruff/format and configured mypy (474 files) pass.
The maintained background Blender capture reproduces the committed fixture exactly.

The public topology workflow, closed guides, transitions/symmetry, reference deformation,
fitting and export are still pending. This checkpoint does not qualify release 0.4.0.

### Closed guide preparation checkpoint

Closed accepted Fiber paths now have batched native projection, graph closure,
192-point arclength sampling, duplicate suppression, symmetry classification and
nested-loop pairing. Capture keeps source/rule identities and accepted Manual paths,
independently of visibility or the backend. Open paths do not become LOOP guides.
Unpaired/collapsed projected loops return explicit diagnostics. The existing native
FLOW shortest-path implementation is reused; point-index ownership is shared between
skin numerical stages rather than duplicated. No authored path is changed.

Three background addon controls cover planar/curved projection and a large closure
gap. Pairing, source identities and statuses match; maximum coordinate difference is
below 1.85e-7. Eight curved-surface samples have different normals at shared edges;
qualification verifies both normals belong to incident triangles within 3e-6 position,
rather than loosening all normal checks. Evidence: `build/skin-040/loop-parity.json`.
Rendered/inspected `build/skin-040/ui/loop-parity.png`. Twenty-five focused ownership,
refinement, loop, workflow and architecture checks pass; native build/five CTests,
selected native style, Ruff/format and configured mypy (476 files) pass.

Next: construct direct/planar/radial annulus candidates, preserve symmetry, then cut
and stitch the generated topology around them. Current loop preparation alone does
not complete that workflow. Public topology publication, persistent deformation,
shortcut fitting, export and full release qualification still remain.

### Annulus construction checkpoint

Native owned annuli now preserve addon direct/planar/radial selection, projection,
Fourier smoothing, orientation, inversion metrics and both symmetry policies. The
unchanged SciPy 1.14.1 assignment kernel is pinned with source hashes/notices; inputs
are bounded to <=96 columns per ring and run on the existing worker. Numerical patch
buffers remain native for the upcoming cut/stitch stage; snapshots carry provenance.

Six direct addon controls select the same methods and match coordinates within 1.21e-6,
with matching connectivity and inversion counts. Reordered/coincident stress guides
exercise fallbacks but do not qualify anatomy. Nineteen focused annulus/loop/architecture
checks pass. Native build/five CTests, selected clang-tidy, Ruff and configured mypy
(477 files) pass. Inspected the rendered overlays in `build/skin-040/ui/annulus-parity.png`.

Next: cutting, transition rings, assembly and backend orchestration. Public topology,
persistent deformation, shortcut fitting, export and complete release qualification
remain unfinished. No version bump or main merge; preserve the root __init__.py.

### Guide holes and transition kernels checkpoint

Ported addon guide-hole masks (PCA footprint, depth/radius limits, 1.08 side scale and
1.0 centered scale), ring alignment, balanced zipper quads, sparse seam candidates,
staged fallbacks and centered symmetric transitions. Shared ring projection now serves
both nested-loop pairing and hole cutting. Native transition bundles preserve polygon
region/guide labels and boundaries. Sources remain unchanged. Quality checks use the
existing triangulation and libigl triangle intersection predicate; compact fixture
agreement does not yet establish all Blender BVH edge-case equivalence.

Twelve hole selections exactly match addon face membership. Ten transition cases cover
sparse/staged/centered results, odd half-strip parity, multistage ratios, quality fallback,
and parity/wrong-side rejection. All eight successful cases match coordinates within
9e-16, exact connectivity and quality diagnostics; the two rejected cases match reasons.
Thirty-three focused tests pass; native build/five CTests, selected style, Ruff and
configured mypy (478 files) pass. Inspected `build/skin-040/ui/stitch-parity.png`.

The combined topology assembly is next. A draft `skin_stitch_orientation.cpp` exists
locally but is not compiled or qualified yet; it is intentionally excluded from this
checkpoint. Public topology integration, symmetry output, reference deformation,
fitting, export and full release acceptance remain unfinished.

### Complete assembly checkpoint

The prior orientation draft is now compiled and checked. Added complete native
assembly, paired transition mapping, welded provenance and Blender-derived outward
orientation. Fixed swapped guide/transition labels before public integration. Exact
Blender float materialization of accepted annuli resolves observed symmetric zipper
tie differences; construction calculations stay double precision.

Six maintained addon fixtures cover side/centered/mirrored joins, strict parity error,
the explicit unstitched warning and disconnected closed shapes. All five successful
controls match positions, oriented connectivity, labels and diagnostics exactly.
Evidence: `build/skin-040/assembly-parity.json`; inspected
`build/skin-040/ui/assembly-parity.png`. Cancellation and owned-output tests pass.
Native build/five CTests and selected clang-tidy pass; configured mypy passes 478 files.
The prior broad gate predates these kernels; full regression remains pending.

Next: symmetry input/output, backend orchestration and public topology jobs/UI. Durable
reference/deformation, shortcut fitting, OBJ export and complete release qualification
remain unfinished. Keep 0.3.7 package version, feature branch and unrelated __init__.py.

### Native symmetry preparation checkpoint

Added owned half-mesh preparation, planar cut-quad beauty triangulation, reflected
output with near-boundary snapping/cap exclusion/welding, and native clipping of FLOW
path runs. Samples and region ownership remain intact. Production source inspection
confirmed `fill_unmatched_boundaries` is a prototype helper, not called by the current
addon solver; do not accidentally add it as an automatic repair.

Seven captured controls match nondegenerate oriented connectivity. Six have exact
positions; the oblique cut differs by at most 1.69e-7 fixture units. At a plane exactly
on a source face, Blender creates 12 duplicate zero-area cut triangles; the native
adapter omits them and retains the same two valid surface triangles. This intentional
structural sanitation is recorded rather than claimed as full index parity. Inspected
`build/skin-040/ui/symmetry-parity.png`; metrics in `symmetry-parity.json`.
Eleven focused symmetry/architecture tests pass, as do build/five CTests, selected
native style, Ruff and configured mypy (479 files). Wider regression remains pending.

Next: bounded Instant Meshes process adapter and complete topology orchestration.
Public topology, deformation reference/LE/FAST, fitting, export and release remain open.

### Topology integration checkpoint — still under qualification

Added bounded Instant Meshes execution through the ordinary executable's private numerical
worker entry point, sharing OBJ exchange and result contracts with QuadWild. Runtime launcher
is shared with report rendering. Instant's native options match the addon; no Qt dependency or
backend substitution. Both remeshers retain process-tree cancellation and limits.

Connected complete topology preparation/assembly through `skin.build` and
`skin.topology.build`, plus desktop buttons. Shared skin stage policies now use one job lifecycle
for reservations, dispatch capture, provenance, atomic publication and initiating undo. Native
helpers resolve the root-local symmetry plane and adaptive initial quad count. Preliminary
integration: 22/23 topology/density/symmetry/architecture tests pass; the non-symmetric QuadWild
case failed. Existing envelope/Instant/architecture checks: 8 passed before the latest changes.
Do not describe these as complete topology qualification.

Investigation found remesher OBJ output was using the user-import tessellator, rejecting folded
generated quads before advisory quality validation. An evaluated-output importer now reuses
existing generated tessellation while retaining finite/index/arity checks; build/test pending.
A second reproduction produced a triangle in QuadWild's smoothed result; this is genuinely
malformed and must not be accepted or silently substituted. Capture:
`build/skin-040/anthroforge-topology-cryg9m4b`. Resolve/qualify this before advancing.

Windows intermittently reports error 112 on larger E: writes despite ~75 GB reported free;
C: writes and small E: writes worked. Deleted only the disposable `build/write-probe.bin`.
A later 1 MiB E: probe succeeded. Native rebuild now runs serially to reduce pressure.
No projects, source fixtures or delivered distributions were removed. Keep root __init__.py.

Next: complete backend/quality qualification, background visual inspection and lifecycle tests,
then persistent reference/deformation, fitting, export and full release acceptance. No version
bump or main merge. Current source changes are an incomplete feature-branch checkpoint.

### Topology quality and isolated proxy checkpoint

The native build now succeeds using temporary outputs at
`C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native`; all five native CTests pass.
E: still intermittently rejects writes with error 112/Errno 28 despite reported free space.
Use `ANTHROFORGE_NATIVE_LIBRARY=<that directory>/bin/af_native.dll` for tests, C: logs,
and pytest `-p no:cacheprovider` until the drive issue is resolved. Do not delete user assets.

Generated-output import is now qualified: folded generated quads retain their vertices and
connectivity; malformed arity, repeated indices and invalid indices remain errors. Full and
symmetric QuadWild and Instant public builds pass, including coherent undo and round trips.
A captured malformed QuadWild calibration output is also rejected by the addon's reader;
this is a retained backend limitation, not a new automatic repair or fallback.

Added native advisory topology diagnostics with accepted-revision Issues evidence. Eight
captured addon controls agree for finite/quad/component/orientation/manifold/degeneracy/valence
checks. Geometry is not changed by diagnostics. Fidelity reports distances (not squared
 distances); unavailable self-intersection checks remain explicitly null. Instant CPython
3.12 output matches the addon's isolated CPython 3.11 geometry/connectivity within 1e-6.
Fixtures and maintained capture tools are committed; visual integration review is next.
The existing native adaptive base-count implementation is reused; the duplicate helper from
the prior checkpoint was removed.

Factored isolated numerical process ownership for Instant and tetrahedral proxy preparation.
PyTetWild uses source numerical settings with one worker thread under the existing process
budget/cancellation contract. Its nanobind function is positional-only despite named stubs;
the adapter is tested on the installed pinned version. This is proxy preparation only, not
reference/LE/FAST publication. No solver fallback or new public operation is introduced yet.

Verification: topology suite 47 passed, one tetrahedral adapter test initially failed; after
correcting that binding, all three proxy tests plus both architecture checks passed. The first
48-dot run could not finish pytest's E: cache write and is not counted as a complete test run.
Native style passed on changed importer/diagnostics. Broad regression, real anatomy, GUI,
reference/deformation/fitting/export and portable release remain pending. Preserve __init__.py.

Recovery note: E: also rejected Git loose-object writes. Removed 282 disposable `.obj`
compiler intermediates (33.5 MB) under verified `build/dev`, after the complete C: build
and native checks succeeded. Kept libraries, dependencies, source and all user artifacts.
Git writes then succeeded. The E: development object files will rebuild when needed.
