# AnthroForge 0.2.0 construction objects

- Task branch: `codex/020-construction`
- Integration branch: `main`
- Starting revision: `b539697`
- Status: in progress; not release-ready
- Last updated: 2026-10-19, Europe/Bucharest
- Recovery update: 2026-10-19. Earlier checkpoint sections below are historical;
  the latest checkpoints supersede their incomplete-feature statements.
- Active writer: local desktop implementation chat

## Outcome and acceptance

Implement the approved [0.2.0 specification](../specification_020.md) and
[implementation plan](../implementation_020.md). Includes first-class curves,
reference images, fibers and curve-based surfaces in desktop and headless use.
Muscles and soft tissues belong to 0.2.1. Preserve the unrelated root `__init__.py`.

## Current state

Consolidated specification and plan are committed. Baseline docs link to the superseding
contract; the previous Free/Controlled normative paragraph now describes curve engines.
Added typed construction objects, Fiber subclass/binding cardinality, generic registry,
distinct parenting/membership validation, incremental construction changes and schema 3
round trips. Old schemas are rejected. Primitives now store CurveUse references; owned
ResolvedPrimitive inputs exist only at evaluation/edit presentation boundaries. Primitive
creation, point/handle editing, duplication, deformers, deletion, dependencies, scheduling
and existing desktop authoring projections use these references. Generic curve creation/
point edits, object rename/transform/reparent/delete/inspect, primitive.from_curves,
primitive.curve_mode and primitive.make_independent are integrated with shared commands.

Native owned paths now evaluate BEZIER and exact POLYLINE, preserve closed-path starts,
omit duplicate endpoints, and retain allocations through read-only array leases. Resources
have typed mesh/path/image catalogues, retained across history/checkpoints/jobs and snapshots.
Schema 3 stores path buffers and deduplicated embedded PNG/JPEG sources; Pillow is promoted
to a runtime dependency and applies EXIF orientation once without Qt. Save/inspection callers
use complete resource snapshots. Native path/typed-resource tests and style checks pass.
Coordinated path jobs now publish accepted buffers/provenance and drive primitive consumers.
Manual source edits retain accepted construction (including inputs for control deformers),
report pending upstream state, and reevaluate live consumers after explicit path publication.
Native sampling reuses accepted paths and preserves existing body/loft sampling behavior.
Curve jobs use the common cancellation/history/checkpoint contracts and task Issues.
Generic workspace associations determine curve editability and task priority.
Profiler memory snapshots now include typed mesh/path/image totals and per-kind ownership,
with bounded native path enumeration, weak job observations and bounded catalogue/history
collection. Disabled profiling performs no inventory queries. Image resource identity avoids
hashing image payloads during observations; reports contain sizes and provenance, not pixels.
Standalone curves have Construction navigation, shared editing, staged display and picking.
BEZIER/POLYLINE/ROUTED engines, native drawing/fitting, images, Fiber attachment deformation,
current-shape editing, explicit junctions and generic loft/patch/branch surfaces are integrated
with desktop controls and the shared API. Routing includes native warm-span remapping and
actual skull donor parity. Authored-engine collision checks use the read-only Issues service.
Direct control.attach is retired; shared controls use ordinary transform relationships.
Source and offscreen qualification has passed; version metadata is now 0.2.0 for portable
candidate packaging. The release remains unmerged until relocated package checks pass.
The current coordinator, attachment kernels, Issues, profiler, transactions and
staged renderer must be extended at their owning boundaries, not duplicated.

## Verification

Read-only inspection completed; `main` and fetched `origin/main` both at `b539697`.
Current shared-curve increment: `uv run --no-sync pytest -q`: 573 passed (32 new cases).
Owned path/resource checkpoint: 586 tests passed, Ruff and mypy pass; native build/contract
and clang-tidy on the modified curve/path implementation pass. Full gate on this increment
has not yet run; the preceding shared-curve full-gate evidence remains scoped below.
Coordinated accepted-path increment: `./tools/check.ps1` passed with 596 tests, full native
style/build/contract checks, Ruff, mypy, numerical imports and doctor. Includes exact old/new
native sampling comparisons for transformed open/closed lofts and body deformation; this is
not a claim of complete new fiber/drawing/surface Blender parity or interactive acceptance.
Resource attribution increment: 598 tests pass, Ruff/mypy pass, native build/contract and
modified native inventory clang-tidy pass. No new full-gate or GUI qualification claimed.
`./tools/check.ps1` passed on the shared-curve checkpoint: native build/contract, native
and script style, Ruff, mypy, all 573 tests, numerical imports and doctor. 0.2.0 GUI/package
qualification has not run. One earlier full run saw the existing global native-allocation
count test change during collection; targeted and subsequent full run pass. Investigate
resource ownership if this recurs; do not weaken the allocation assertions.
An initial suite overlapped source editing and its subprocess saw an intermediate invalid
dataclass definition; it is not baseline evidence. Subsequent checks used stable content.
No visible applications or desktop input permitted while the user is gaming.
Use background/offscreen checks and state their limits.

## Next actions and blockers

1. Finish active documentation, API examples and package notices for the complete workflow.
2. Run the stable integrated offscreen suite, development gate and ownership/coupling review.
3. Build and qualify the relocated portable executable, headless and invisible rendering,
   before the versioned release/source archive and validated merge. No interactive acceptance
   may be claimed while validation is background-only.

Important findings: ordinary parenting and consumer frames need an atomic rebind to avoid
double transforms after a new shared ancestor is introduced. Local path/local-pose ports
must not depend on the consumer's world pose, otherwise a pure SCP transform unnecessarily
obsoletes geometry jobs. `consumer_parenting.py` and shared-curve regression cases cover
these boundaries. Newly created primitive children now capture their origin attachment
through the existing evaluation contract. Profiler changes include construction-object
fields (e.g. points), not a fictitious change to the primitive reference definition.
Path prerequisite admission must avoid inline publication before its consumer is registered;
queued consumers already waiting on that path are retained rather than superseded. Regression
coverage preserves the first construction job during an SCP pose edit. Generic paths retain
analytic tangents; Blender body deformation separately reconstructs bevel tangent bisectors.
Sharing the body-specific tangent preparation with loft sampling caused a measured parity
difference and was corrected at the native frame boundary, not by relaxing tolerances.

## Recovery inputs

Normal Windows environment and native toolchain already exist in this checkout.
Addon migration reference: `C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
Original geometry references remain under `E:/development/WIP_models`; do not commit
large source assets. Copy compact reproducible fixtures with source provenance.
Push every coherent checkpoint; incomplete work stays on this branch.

## Standalone editor checkpoint

Construction has its own incremental list and selection records. Existing point/handle editing,
transforms, insertion previews and undo now accept standalone curves. Generic inspection reports
path resources, ordinary parents and source-consumer topology locks without an anatomical proxy.
Object transforms accept an explicit world-space request and resolve ordinary parent-local state.
Resolution changes through both primitive and source APIs enforce the shared lock. Construction
visibility/pickability can be stored independently. Keyboard deletion resolves construction objects.

Validation: 602 tests pass; Ruff and mypy pass. `tools/construction_editor_acceptance.py` loads the
actual desktop QML on the offscreen platform and exercises standalone selection, inspection,
framing, point drag/undo, insertion and canceled transforms without warnings. This is controller/
QML acceptance only: no visible desktop input, full interaction rendering or package acceptance.
Curves still need staged native display/picking outside edit mode. Image/fiber/surface production
workflows, drawing, complete Construction controls, legacy control-attachment retirement and
release qualification remain incomplete. Do not release or merge this checkpoint as 0.2.0.

## Native path presentation checkpoint

Native accepted paths now own bounded float render chunks and a segment AABB index, built
before publication. Batched picking uses world-space distance with exact nonuniform/reflected
transforms and cached local trees. The existing staged renderer now accepts explicit resource
leases; paths use their own handle namespace/model and switch picking to the displayed revision.
Profiler viewport ownership includes path leases and native inventory includes derived buffers.
A native single-affine-instance adapter preserves shear from ordinary transform parenting instead
of discarding it through TRS decomposition. Curve category visibility/pickability is respected.
Empty-document presentation uses the generic object registry rather than only the anatomical tree.

Validation: 608 tests pass, Ruff/mypy pass, native build/contracts and changed-native clang-tidy
pass. `tools/path_scene_acceptance.py` renders the actual viewport through QQuickRenderControl
into a D3D11 texture without a visible window. Hover/click results agree; replacement retains
old buffers and releases them after activation; a pixel check verifies a rotated path under a
nonuniformly scaled ordinary parent. Captures were inspected in build/020-path-scene. Generic
Qt offscreen QPA could not initialize D3D11, so this render check uses the platform backend with
an explicitly invisible render-control window. No desktop input or interactive acceptance.
The controller/QML standalone editor acceptance also passes. Full 0.2.0 remains incomplete.

## Image authoring checkpoint

Extracted the existing mesh-import history/publication behavior into `authored_jobs`; mesh
and image imports now use that shared contract. Added background PNG/JPEG decoding with
EXIF orientation, cancellation, independent image instances sharing embedded assets, source
replacement, physical sizing and native two-landmark calibration. Import completion belongs
to its initiating undo step even when later edits exist. Completed same-source replacement
is not restarted by redo. Native image resources own bounded 256-pixel texture tiles; Qt
adoption is limited to one tile per staged item. Display/interaction integration is next.

Validation: full native build/contracts pass, changed-native clang-tidy passes, Ruff/format
and mypy pass, and 617 tests pass. Includes image-only documents, aspect/width preservation,
instance independence, transformed calibration and undo, interrupted import undo/redo,
embedded persistence without the original source, invalid input, and existing mesh-import
regressions. The full development gate passed on the preceding path checkpoint (608 tests).
No image rendering, interactive acceptance, or 0.2.0 packaging acceptance is claimed here.

## Image presentation and editing checkpoint

Construction now exposes image import, source replacement, shared-asset instances, numeric
size/transform, ordinary parenting, world-axis alignment and two-landmark calibration.
Per-workspace image appearance includes opacity, depth, side visibility, projection modes
and pickability. Native plane picking uses displayed dimensions/provenance and current view
projection. Images have their own staged model and asset leases, included in profiler owners.
Native image quads preserve affine transforms without decomposing shear.

Validation: 624 tests pass; Ruff/format/mypy pass; native build/contracts and changed-native
clang-tidy pass. Texture-only D3D11 checks in `tools/image_scene_acceptance.py` cover exact
quadrant orientation, hover/click, front/back/normal occlusion against a cube, calibration
with one-action undo, complete old-image retention during replacement and lease release.
Captures in `build/020-image-scene` were visually inspected. Path rendering regression and
offscreen construction-editor checks pass. No visible windows or desktop input were used;
interactive and packaged acceptance remain unperformed. The full development gate passed.

Diagnostic findings: instanced custom image quads were invisible in this setup; normals and
indices did not fix it. Non-instanced quads with six native-transformed vertices render
correctly. Reparenting existing nodes between View3D scenes lost display; staged filtered
layer models preserve it. These findings and ownership boundaries are in architecture.md.
Remaining release work still includes native drawing/fitting/cursor, conversion previews,
complete consumer/navigation controls, fibers/routing/attachments/junctions, generic surfaces,
legacy control-attachment retirement, performance evidence and full release qualification.

## Ordered sources and consumer controls checkpoint

Object selection now preserves selection order, with extension handled through the existing
keyboard abstraction. Creating a primitive from selected curves keeps live references in that
order. Inspectors expose usage, transform-consumption mode, reverse direction and Make Independent.
The document registry owns the shared reverse consumer index, avoiding repeated full scans in
usage queries. This is a structural improvement; no timing improvement is claimed without profiling.

Validation: 626 tests pass, including consumer-index changes across independence/deletion/undo
and reversing one consumer without changing its source or other consumers. Offscreen full-QML
checks cover ordered creation, usage projection and selection pruning. Ruff, configured mypy
and function-length checks pass. An exploratory `mypy src` invocation also checked desktop
modules outside the configured gate and reported existing untyped-adapter errors; it is not
the repository's type-check command. Full development gate passed immediately before this
Python/QML-only increment. Drawing/cursor and the remaining release work above are still pending.

## Native fitting checkpoint (desktop integration in progress)

Vendored Blender 5.0.1's unchanged BSD curve_fit_nd C kernel with hashes/notices and a narrow
C++ adapter. REFIT/SPLIT fitting, corner handle modes, closure, optional radius channel and exact
polyline creation share one owned-output boundary. `curve.draw` fits and prepares the accepted
path on a dedicated coordinator policy, then uses shared async authored publication. Parent
validation/placement was extracted from images into object_creation for both clients.

Native build/contracts, changed-native clang-tidy, Ruff/configured mypy and 11 focused drawing/
architecture tests pass. Tests include shape error/endpoints, closure, cancellation, interleaved
undo authorship and persistence. Image import regressions passed during the extraction. Full
suite is pending for this increment. This is not completed Draw UX: stroke projection, cursor,
desktop input/preview, actual Blender operator parity and performance evidence are next.
The kernel cannot cancel internally; measure its atomic interval before claiming responsiveness.

## Drawing/cursor integration checkpoint

Added native owned stroke projection/sampling with surface snapshots, last-valid-depth fallback,
normal offsets, radius-relative offsets, first-hit view/surface planes and view rebasing.
Desktop Add Curve, Place Points and Draw use shared authoring; completed draws fit asynchronously
and remain one undo action. Draw stays ready for another stroke. Cursor coordinates are persisted
workspace presentation; curve creation resolves their world position even under ordinary parents.
Reference-image tracing captures a plane without an enduring image reference.

Six compact fixtures captured with Blender 5.0.1's actual background Draw operator pass native
parity (open arcs, corners, closed loops; REFIT/SPLIT). Reproduction is in capture_drawing_parity.py;
the preserved source is build/reference-fixtures/blender501_drawing.blend (ignored local artifact).
Offscreen full-QML checks cover repeated drawings, point removal, cancellation and one-action undo.
Texture-only drawing_scene_acceptance.py verifies preview/final display, pixel/picking agreement,
and independence after image deletion; captures were inspected. Image/path rendering regressions
also pass. No visible windows, desktop input or interactive acceptance were used.

The texture check exposed a flattened top-view path despite correct authored/native coordinates.
Explicit instanceRoot did not fix it. PathScene now supplies the complete application-to-display
coordinate matrix outside the anatomy rotation node; top-view and affine-parenting pixel checks
pass. Earlier path checks did not cover this view and were insufficient evidence for it.

A runtime report is at build/020-drawing-scene/drawing.afprofile.zip. Its small tracing fixture
shows native fitting separately (~0.66 ms), path preparation (~0.11 ms) and pointer projection
(~0.01–0.02 ms). This is attribution evidence, not a responsiveness benchmark: texture readback
and scripted pauses dominate frame intervals, and Qt binding profiling was not enabled here.
Larger fitting/cancellation trials, complete drawing option parity/headless projection operations,
engine conversion, routing/fibers/surfaces and release qualification remain required.
Full development gate passed: 648 tests, native contracts/style, Ruff, configured mypy and
headless dependency checks. The earlier error-message regression is corrected.

## Shared drawing projection follow-up

Added `drawing.project` for Qt-free clients using the same native owned stroke projection
as desktop input, including Blender's tangent-view first-hit plane. Batched projection runs
its repeated queries in C++, supports cancellation and restores the provisional stroke on
failure. Desktop settings now validate before adoption; preview-owned buffer capacities are
reported separately from shared mesh leases in profiler inventories.

Native contracts, changed-native style, 23 focused checks, configured mypy and the full-QML
offscreen construction editor pass. `tools/drawing_qualification.py` produces measurements
and an ordinary profiler report under build/020-drawing-qualification. Serial trials measured
1k samples at 2–9 ms, 10k at 52–96 ms and 100k at 840–1263 ms. Cancellation requested at 20 ms
returned after about 1509 ms in the largest smooth trial, rejecting output. The kernel's atomic
interval is an observed limitation, not a claim of immediate cancellation or a UI-frame test.
These are single-fixture trials with profiling enabled, not a controlled speed comparison.

## Typed engines and explicit conversion checkpoint

Curves now own typed engine settings; Bézier sampling, exact polyline and routing configuration
are separate records. The API's existing Bézier resolution command resolves to that setting.
Persistence, primitive adapters, UI projections and fixtures were migrated together. Routing
configuration does not expose an implementation generation; native routed evaluation is next.

One bounded conversion preview uses read-only coordinator work and explicit input revisions.
It does not author or block saving. Accept checks shared topology locks and freshness, preserves
current metadata and accepted geometry, and commits through ordinary operations. Preview paths
use staged publication and retained leases, appear green and are unpickable. Cancellation and
project adoption release preview ownership. Profiler ownership includes the preview resource.

Nine behavioral tests cover history, stale rejection, closed correspondence, shared locks,
explicit routing constraints, ownership release, typed persistence and cancellation. Full-QML
offscreen checks and texture-only preview/accept/undo checks pass; conversion-preview.png was
visually inspected alongside pixel assertions. No visible-window interaction was performed.
Ruff, mypy and function-length checks pass. Last full pytest run before conversion had 652
passing behavior tests plus a length-check failure, corrected; the complete gate is next.

Remaining: routed engine/native preparation, attachment deformation and fiber creation/editing,
junctions, generic surfaces, control-attachment retirement, complete performance/lifecycle
qualification and portable release. Conversion with interior fiber bindings will need preserved
constraint correspondence; current sampled conversion requires authored mode for those inputs.
Version stays 0.1.9 and this checkpoint is not a 0.2.0 release.
The subsequent complete development gate passed with 662 tests.

## Shared anatomical point attachment kernels (fiber integration pending)

Inspection found that addon fibers bind all committed nodes to nearby anatomical surfaces,
then retain bind-time C2 owner transitions along hard-pin-partitioned arcs. This behavior is
more than interpolating endpoint displacement. Ported the Python owner-weight numerical loops
to C++; 11 extracted addon reference cases agree, including uneven/cyclic/zero-length spans.

Added batched generic point capture/resolution to the existing attachment library, reusing
canonical 28-value attachment records and the unchanged surface-frame kernel. It accepts
forced or nearest eligible targets at capture and never changes owners at resolution. No
document SCP proxies are created. Native cancellation and transformed-surface preparation stay
within the batch. Python packs inputs and unpacks records only.

Native build/contracts, changed-native style, configured mypy and 90 focused tests pass.
The tests include existing SCP/Blender attachment parity, point round trips under reflected
nonuniform transforms, fixed-owner propagation, geometry changes and cancellation. This is a
qualified kernel increment, not a completed fiber workflow. Fiber creation, dependency reads,
current-shape editing/rebinding, routing and surface consumers still need integration.

Before selecting the fiber shape-binding representation, preserve the distinction between the
addon's dense committed-node bindings and editable Bézier knots/handles. Do not claim dense
deformation parity from a control-point-only approximation. Inspect/qualify that integration
against actual addon fixtures. Routing uses the current production facade in
core/vcp/v3/production.py; its native SQP controller already exists, while Python still owns
numerical planner/span preparation that must move behind the new native boundary.

## Dense fiber capture and propagation checkpoint

`fiber.create` now makes an independent actual `Fiber(Curve)` through the shared asynchronous
creation/history contract. Both open endpoints or at least one closed authored point must bind.
A native field captures every evaluated node plus editable control triples, retains the addon's
arc-length owner blending, and resolves current anatomical surface frames in a single batch.
Candidate compaction and repeated numerical work stay in C++; no dummy SCP is created.

Separate attachment resources retain their bind-time path and typed immutable arrays. They are
serialized in schema 3, collected across history/checkpoints/jobs, and attributed in profiler
inventories. Native frame and owner validation rejects malformed inputs. A shared dependent-output
fan-out now reaches paths as well as controls and meshes after anatomical pose/geometry publication.
Mesh and path result provenance share the same pending-Manual-input policy. Incoming fiber support
bindings participate in topology locks and anatomical deletion protection.

The desktop inspector exposes explicit surface choices and independent creation through the same
command. Offscreen full-QML testing invokes its actual action, checks Construction/path publication,
and selects the resulting Fiber. This found and fixed a QML id collision with Item.anchors that
otherwise omitted the last mandatory endpoint. No visible desktop interaction was performed.

Focused checks cover independent identities, one-action undo/redo, open/closed dense-node parent
motion, source preservation, archive round trips, cancellation, typed buffer validation and native
weighted deformation. Existing construction-editor offscreen checks pass. Native build/contracts,
configured mypy, Ruff and function-length checks pass at this checkpoint; full gate is next.

This is still incomplete 0.2.0 development. Fiber current-shape editing/rebinding, routing,
junctions, generic surfaces and final release qualification remain. Do not treat control-triple
capture as a substitute for dense-node attachments or claim full addon shape parity from the
translation/owner-weight tests. Do not bump the version or merge the release yet.

## Current-shape fiber editing checkpoint

The preceding complete development gate passed with 686 tests. Current-shape fiber editing is
now integrated through the same point commands, including edits presented through primitive
consumers. Entering edit mode queries accepted resolved controls without changing document state.
An explicit edit retains its accepted baseline and candidate surfaces while work is pending.
Native correspondence rebases the authored engine's change over the currently deformed dense
path, then captures new bindings. Unedited anchor records remain exact; edited endpoints either
stay on their current parent or choose any eligible parent according to the shared scope policy.

Publication installs the complete path, controls, captured relationships and attachment resource
without incrementing the authored-change revision. Pending baselines participate in serialization
and resource reachability. Cancellation and undo restore the previous path and attachment field.
The inspector exposes endpoint capture scope; its actual desktop transform path is exercised in
an offscreen QML check after anatomical parent movement.

Six new behavior checks cover non-mutating editor queries, current-shape interior edits, retained
anchors, parent motion after rebinding, cancellation, Any-parent selection and point insertion.
62 focused checks, configured mypy, Ruff, Python limits, changed-native style, native contracts,
and both offscreen construction/fiber editor checks pass. No visible-window acceptance performed.

Remaining fiber work includes adding/removing/reassigning structural bindings, complete topology
and conversion cases, routed evaluation, collision diagnostics, junctions and representative
addon parity/visual qualification. The deformation residual used for native authored engines is
an explicit adaptation to editable Bezier/polyline controls; addon Free paths store all sampled
points. Do not claim that every edit/rebase or routing case is already qualified. Generic surfaces,
control-attachment retirement and full 0.2.0 release qualification also remain.

Follow-up qualification found that the structure-cache signature omitted dense support references.
It now derives construction links from the shared dependency policy, so new internal surface
owners participate in invalidation and cycle checks. A regression test moves a newly captured
internal support while both explicit endpoints retain their original parent. Automatic capture
excludes surfaces generated downstream from the same curve; otherwise editing a fiber consumed
by a body could create an unintended self-dependency. Explicit cycles remain diagnosable.

Fiber path work has its own conservative worker scheduling policy, estimating dense record count
and recapture triangle workload instead of using the cheap ordinary-curve inline threshold.
Two additional tests cover consumer editing and newly captured support invalidation. The latest
focused checks and desktop gesture acceptance pass; full development gate follows this checkpoint.

## Fiber consumer deformation qualification

The preceding full gate passed with 694 tests. A new differential-support fixture
reproduced a consumer defect: adding an unmoved curve Hook changed 960 of 1446 body
coordinates (maximum displacement component 0.2281). Consumer control deformation
was rebuilding the authored engine path and discarding accepted dense deformation.
It now applies the control deformation delta over the accepted path in native work,
retaining correspondence and unchanged frames. This is a shared curve-consumer rule,
not a Fiber-specific exception. The regression and 115 related primitive/parity,
fiber-editing and architecture checks pass; mypy, Ruff and changed-native style pass.
Routing migration is next. Full routing, binding lifecycle, junctions, general surfaces
and the remaining qualification recorded above are still unfinished.

## Native routing migration checkpoint (not yet exposed as a complete engine)

Pinned the production addon's collision/contact/SQP numerical closure with source hashes
and reproducible extraction. Native adapters capture owned surfaces, transforms, scales,
reference nodes, hard-pin span sessions, closed global solve state, cancellation between
trials, path output and diagnostics. Python only packs the call. No Blender runtime or
second worker pool is introduced. Existing application routing remains explicitly unavailable
until integration and the complete planner contract qualify.

Ported initial direct/compatibility/projected-surface preparation and exact corner-preserving
handoff. A cube-detour test first failed because uniform resampling cut planner corners;
porting the addon's allocation/handoff semantics resolved that difference. Four actual-addon
fixtures now agree to absolute 1e-10; native cancellation/membership/open/closed checks pass.
18 focused checks, mypy, Ruff, function limits, native build/contracts and changed-native style
pass. The complete sparse/dense/expanded/pin-exit planner, warm inputs, failure diagnostics,
application/desktop routing and representative anatomical qualification remain required.
Do not claim these four small fixtures establish all routing acceptance.

This checkpoint also fixes the fixture helper's formatting-induced function-length failure.
Version remains 0.1.9. Full gate is pending this kernel increment; no visible UI was used.

## Native planner continuation

The full Python suite passed with 702 tests after correcting a process-wide inventory
test's measurement boundary: collect unreachable objects before paired snapshots and
temporarily exclude GC between them. Exact alias and byte-deduplication assertions remain.
The preceding full gate reached pytest; rerun the complete gate after this increment.

Native preparation now includes mesh-surface routes, sparse/dense shells, owner exit
access, expanded roadmaps, and bounded deterministic pin-exit recovery. The accepted
addon tree fixture was captured without Blender: all 1,050 nodes, parent indices and
the final path agree within 1e-13 in the native test. PCG64 and bounded integer behavior
are pinned to NumPy 1.26.4 with upstream notices; no Python numerical loop is retained.
Cancellation is checked between collision queries and graph-neighbor preparation rows.

Inspection found the donor lazy graph allocated count-squared metric and state arrays.
The adapter now stores only actual graph edges and shared undirected collision proofs,
retaining A* ordering and lazy validation semantics. This structural memory improvement
still needs representative workload measurement and broader route parity qualification.
Native build and tree contracts pass; focused Python checks and native style pass for
the preceding planner changes. Sparse-search follow-up validation is in progress.

Routing is still not application-integrated. Warm inputs, independent handoff validation,
diagnostic publication and representative anatomical qualification remain. Binding
lifecycle, junctions, generic surfaces and the other release work above remain open.
Do not label this checkpoint a completed 0.2.0 release.

## Routing application integration checkpoint

Routed standalone curves and fibers now evaluate through the shared path pipeline.
Declared obstacle/support pose and geometry inputs participate in dependency invalidation,
full revision validation, worker-only scheduling and retained-output failure handling.
Warm path capture is native; pins are replaced by current authored constraints. Routed
fiber edits rebind authored constraints before solving rather than treating sampled output
as editable knots. Conversion previews include new obstacle inputs and fiber capture
candidates in their read sets. Accepted routing diagnostics round-trip with path resources.

The shared `curve.engine_settings` operation edits the existing engine's settings without
bypassing previewed engine conversion or consumer topology locks. The desktop inspector
exposes sampling, clearance, solve budget and explicit obstacles. Offscreen full-QML
acceptance invokes the actual obstacle checkbox, verifies authored-point selection,
gesture editing/undo and staged path output. No visible window or desktop input was used.

35 focused routing, conversion, fiber and architecture tests pass; Ruff and configured
mypy pass. The desktop check passes. Native warm support builds and both native contracts
pass. Full gate follows this checkpoint. Still required: independent planner handoff
validation, broader routing/warm parity and representative performance/geometry evidence,
remaining binding/conversion cases, junctions, surfaces and all final release work.

## Independent planner validation

The complete development gate at 51f7ad7 passed with 706 tests, native checks,
style checks, dependency validation and doctor. No interactive acceptance was performed.

Planner handoff now receives the addon's separate static clearance check after
corner-preserving resampling. Native contact intervals walk both directions along
the path, including closed wrapping and overlapping owner exemptions. The check
tests non-exempt nodes for containment and remaining edge fragments for clearance;
rejected handoffs leave the solver's direct-reference attempt intact.
All three native contracts and 11 routing/parity/workflow tests pass. Changed-native
style passes. Broader anatomical/warm qualification and the remaining 0.2.0 workflow
remain required; version is still 0.1.9.

## Fiber binding lifecycle

Shared commands now add, reassign/recapture and remove structural bindings. A chosen
parent with an explicit pending capture is authored state; accepted fields always contain
captured attachments. Requests, current-shape baselines and Manual behavior round-trip.
Open endpoint insertion/removal transfers the mandatory parent choice; closed-to-open
conversion requires both endpoint choices first. Consumer and standalone editors use the
same shape policy. Workspace association includes explicitly chosen anatomical parents.

New tests exposed native frame changes during binding-only edits and a restriction that
rejected endpoint topology edits. Attachment resolution now preserves frames for unchanged
shape/translation; shape correspondence supports endpoint extension/trimming and closure
changes. No-op point edits return before resolving handles, avoiding floating-point-only
changes to authored state. Binding-only edits recapture the resolved path without rebuilding it.

28 focused binding/fiber/routing/architecture checks pass; mypy, Ruff, native build and
three native contracts pass. Changed-native style passes. Full-QML offscreen acceptance
invokes actual Bind/Remove actions plus fiber creation and gesture undo. This is not
interactive visual acceptance. Copy-resource remapping, full interior-binding conversion,
junctions, surfaces, wider parity/performance evidence and release qualification remain.

## Copy and conversion completion

Independent construction copies now remap accepted path metadata, dense attachment target
identities, routing obstacles and pending edit baselines through one resource-copy context.
Immutable native allocations remain shared safely. Manual consumers retain their accepted
path immediately instead of losing geometry while their independent copy is pending.
Tests duplicate an anatomical subtree, move an original support without moving the copy,
and save/reopen a pending copy after authored-point removal before evaluating it.

Sampled engine conversion now preserves interior anatomical binding identities and exact
positions. Native resampling allocates the requested count between required anchors,
including closed wrapping; too-small budgets fail explicitly. This reuses the production
routing edge allocation and existing path interpolation. Open/closed conversion tests retain
bindings, undo and subsequent parent motion. The actual QML Preview/Accept actions also pass
offscreen with an interior binding. No interactive geometry acceptance is claimed.

22 focused conversion/copy/routing/architecture checks pass, plus the earlier 38 shared-curve
checks. Native build, three contracts, changed-native style, configured mypy and offscreen
fiber-editor acceptance pass. Ruff import cleanup is applied. Full development gate follows
this checkpoint. Junctions, generic surfaces, control-attachment retirement, broader geometry
and performance qualification and complete release delivery remain. Version stays 0.1.9.

## Ordinary controls and anatomical boundaries

The full gate at fc4c5a7 passed with 722 tests, native contracts/style, type checks,
dependency validation and doctor (`build/check-020-binding-copy.log`).

Hook/lattice anatomical attachment state and `control.attach` are now removed. Controls
follow eligible ordinary objects through a shared cached transform resolver and cycle guard.
Their dedicated scheduling policy no longer captures all mesh resources to resolve a pose.
Controls appear in Construction; anatomical workspace membership excludes them, while
association and consumer relationships determine their workspace accessibility.

Generic parent deletion preserves world placement and propagates changed inputs through
the shared dependent-task boundary. Origin relocation exposed a geometry-offset/object-frame
confusion: ordinary frames now exclude geometry offsets, and origin changes atomically rebase
ordinary children plus consumer placement. Regression tests cover actual Hook deformation,
curve consumers, deletion/undo, workspace inclusion and rejection of the retired operation.

726 pytest tests pass (9 existing Qt property-map deprecation warnings); Ruff, configured
mypy and the 15-line architecture rule pass. The full-QML offscreen Construction acceptance
checks control navigation, the actual ordinary-parent combo and parent-driven transforms.
No visible window, desktop input or interactive visual acceptance was used. Broader gate,
junctions, generic surfaces, geometry/performance qualification and release delivery remain.

## General surface native kernel checkpoint

Native loft sampling/alignment and loop-patch construction now port the actual addon
Python kernels. Six compact captured cases pin source hashes and outputs, including
irregular closed rows and a concave nonplanar patch. Vertices agree to absolute 1e-10;
polygon connectivity agrees exactly. Native creation/Realign computes correspondence
and transverse density separately from ordinary geometry evaluation. Geometry evaluation
uses supplied correspondence unchanged. The existing primitive loft shares grid topology.

Twelve focused surface/architecture checks pass, including cancellation, range/reversal,
flip, bounded output and retained closed correspondence. Native build, all three contracts
and changed-native style pass. Ruff and configured mypy pass. Surface application jobs,
stable identity serialization, desktop/API creation and editing are not integrated yet.
This is a recoverable numerical-kernel checkpoint, not a completed surface increment.
Junction/branch work, remaining parity/performance and release qualification remain.

## Surface application integration checkpoint

Loft/patch creation and explicit Realign now use asynchronous authored jobs. Stable
point identities retain closed correspondence. Surface geometry uses the existing
coordinator, revision checks, accepted mesh storage and staged renderer. Live, On Release
and Manual tests exposed and fixed a distinction between authored geometry invalidation
and output publication in the shared dependent-task boundary. Generic evaluation Issues
now include construction objects instead of only SCPs/controls.

27 focused surface/construction/architecture tests pass; configured mypy and Ruff pass.
Full-QML offscreen acceptance invokes the actual creation menu, Realign, normals and undo,
with no QML warnings. Consumer settings are projected separately from editable curves.
This verifies desktop entry points and staging records, not GPU visual or interactive
acceptance. No visible window or desktop input was used.

Still pending in this increment: shared Surface consumer reparenting/independence/removal,
queued prerequisites and broader lifecycle/Issues tests, actual invisible GPU render/pick
checks, and a full development gate. Junctions/branches, remaining parity/performance and
release qualification also remain. This checkpoint is not merge-ready; version is 0.1.9.

## Surface references and displayed picking

Primitive and Surface consumers now share source-reference editing, ordinary-frame
rebasing and independent copy policies. Surface copies remap stable closed correspondence;
reparenting, origin changes and deletion preserve placement. Tests cover shared parent
movement exactly once, other consumers retaining the original, and undo after deletion.
Creation registers path prerequisites before layout admission, rejects incompatible source
closure immediately, and supports queued creation/undo/redo. Manual accepted inputs retain
provenance, missing accepted inputs fail boundedly, and generic Issues provide verified
recalculation for failed/pending surfaces. Accepted geometry survives failure.

Invisible D3D11 rendering exposed missed planar/shared-edge ray hits. The native query
adapter reuses the cached BVH with explicit parallel-slab handling and ray-space triangle
edge tests. Both directions on all three axis planes now pass before/after deformation,
including boundary vertices. No ray perturbation, vendor edit or Python mesh scan is used.
See `native/migration/CURVE_SURFACES.md` for evidence and algorithm references.

Surface reference/lifecycle tests, 14 native ray regressions, configured mypy, Ruff and
the architecture rule pass. Full-QML menu, Realign, normals, independence and undo pass
without warnings. GPU texture captures were inspected: loft and edited loft render with
selection outlines. Hover/click agreement, old displayed revision during staging, handle
release and exclusion from anatomical snapping pass (`build/020-surface-scene`). This is
offscreen evidence only. Full development gate follows this checkpoint.

Remaining: junctions/branches, surface source-list editing, authored fiber collision Issues,
per-consumer primitive sampling, drawing parity details, broader anatomy/warm routing and
profiler measurements, resource/history edge cases, examples and full portable release.
Do not merge or publish 0.2.0 until the complete requested workflow is qualified.

The full gate completed native contracts/style, Python types/style and script checks,
then found one Issue-retry regression: object-generic editability rejected document-wide
jobs without a target. The shared repair policy now retains the original document-scope
behavior while using workspace association for object targets. The rerun passes all
765 pytest tests (9 existing Qt deprecation warnings); numerical imports and doctor pass.
Logs: `build/check-020-surfaces.log`, `build/pytest-020-surfaces.log`.

## Junction model and ordinary-curve checkpoint

Authored points carry explicit junction membership; a document Junction identifies its
designated source point. Junctions are relationships, not fake anatomical or scene objects.
The source's accepted path/pose supplies a distinct junction output; incident paths depend
on it without adding a source self-cycle. Actual cycles remain authored and diagnosed.
Schema 3 persists identities, and independent curve copies clear junction membership.

Shared create/remove/inspect commands and point-edit expansion now support ordinary curves.
Point edits update incident authored records atomically; object transforms remain separate.
Engine input resolution consumes accepted source provenance and applies native handle/path
editing, retaining attachment residuals where present. Publication fans out to dependent
paths through the same coordinator. Manual sources retain accepted output until publication.
Sources without junctions keep an early no-op path.

33 focused junction/shared-curve/surface/architecture tests and configured mypy pass; Ruff
passes. Contract tests cover identity, source changes, actual cycles and serialization;
workflow tests cover both-member edits, one-action undo/redo, transform following, detaching
without a jump, deletion protection and Manual publication. This is an incomplete checkpoint:
shared Fiber binding ownership/propagation, conversion anchors, copied-set junction sharing,
desktop junction controls, branches and the other release requirements remain. Do not treat
generic acceptance of a Fiber record as qualification of its shared binding behavior.

### Shared fiber bindings

Junction sources now own the shared anatomical binding on their actual Fiber point.
Joining adopts that binding; explicit assignment/scope edits propagate atomically.
Follower evaluation uses the source's accepted binding, retains its exact native capture,
and recaptures its deformation field only when needed. Manual sources keep accepted
binding provenance until explicit publication. Unbound ordinary points cannot own a
mandatory Fiber binding; the shared policy reports the required bound source.

23 focused Fiber/junction/architecture tests and configured mypy (168 modules) pass.
Evidence covers edits from either member, Any-parent and explicit-parent rebinding,
parent movement without recapture/drift, Manual inputs, mixed Curve/Fiber membership,
one-action undo and save/reopen. Desktop controls, conversion/copy identities, branches
and remaining release qualification are still pending; this is not release-ready.

### Junction interaction and identity

The curve inspector now exposes a collapsed Shared junction section with explicit source
selection, join and detach operations. Full-QML offscreen checks invoke these controls,
verify membership, detach and undo, retain editing/selection, and produce no QML warnings.
No desktop input or visible native window was used.

Sampled conversion preserves shared point IDs/membership; routed conversion requires those
points as explicit constraints. Anatomical assembly copies remap junctions within the copied
set (including accepted path metadata and dependency output IDs), without linking originals.
Single independent copies clear membership. Five focused identity/architecture tests pass;
configured mypy (169 modules) passes. Full suite and branch construction remain pending.

### Native branch and shared API checkpoint

Native branch assembly now ports the actual addon kernel with explicit shared seam IDs,
ordered interior roots, outer-boundary constraints, overlap rejection, station/mesh budgets
and cancellation. Eight pinned donor cases match vertices (1e-10) and faces exactly. Native
build and clang-tidy pass. Uniform sampling retains required root stations.

Surfaces own typed main/branch source groups. Shared API branch add/remove operations retain
source curves, propagate ordinary path dependencies, reject unresolved junction removal,
and round-trip editable branch identities. Application tests cover creation/undo/redo,
shared edits, deletion and save/reopen. 16 native/workflow/architecture checks and configured
mypy pass. Desktop branch controls, invisible visual qualification, source-list edits,
branched-source independence and the previously recorded release work remain pending.

### Branch desktop and independent assembly

The Surface inspector now offers collapsed branch choices derived from explicit junctions,
ordered root selection, removal, undo and a clearly labelled Make assembly independent.
Connected surface sources copy together with new point/junction identities; moving originals
leaves the detached surface unchanged. Schema decoding now restores immutable branch tuples,
and a complete Surface-record roundtrip test passes.

Full-QML offscreen branch add/remove/undo/independence passes without warnings. Invisible
D3D11 captures `build/020-branch-scene/branch.png` and `edited-branch.png` were inspected;
the seam remains connected before and after a shared point edit. Displayed mesh/picking
revision changes atomically and obsolete viewport leases release. This is texture/offscreen
evidence, not interactive acceptance. 23 focused tests, mypy (174 modules) and Ruff pass.

Next: broader gate; surface source-list edits/closed-layout preview, shared authored-job
historical result provenance, per-consumer primitive sampling, authored-fiber collision
Issues, drawing parity details, representative anatomical routing/profiler workloads and
release documentation/examples/package qualification. Keep version 0.1.9 until complete.

### Gate and source/history corrections

At c0e3c02 the full development gate passes: 803 pytest tests (9 existing Qt deprecation
warnings), native contracts/style, PowerShell checks, Python types/style, numerical imports
and native doctor. Log: `build/check-020-branches.log`.

A discriminating queued-input/history test then reproduced a live-reference publication bug:
a surface's latest result was inserted into an earlier undo snapshot with older accepted
source inputs. Surface historical merge now compares the complete read set; earlier snapshots
retain pending authored construction (or their previous accepted result), and navigation
reevaluates them normally. A separate offscreen timing case exposed accepted-shape queries
erasing an unpublished ordinary-curve junction. Queries now retain newer authored state;
a forced-worker two-junction regression passes.

Surface API now supports source add/remove/replacement, preserves existing source settings
and closed correspondence, validates minimum/duplicate/closure constraints, and preserves
removed sources. The inspector shows one source's settings at a time instead of repeating
all controls. Actual full-QML add/remove, branch controls and previous surface operations pass
without warnings. 13 focused source/history/junction/architecture tests pass; configured
mypy (176 modules) and Ruff pass. Full gate has not been rerun after these corrections.

Remaining: closed-loft initial alignment preview, per-consumer primitive sampling, authored
fiber collision Issues, Blender drawing auto-closure/substep details, representative anatomy/
warm routing and profiler workloads, resource edge cases, examples/docs and portable release.
The broader requested release remains incomplete; no version bump or main merge yet.

### Drawing sampling and closure checkpoint

Compared Blender 5.0.1 `editcurve_paint.cc`: corrected native motion filtering and substep
rounding; only fitted surface drawing requests depth substeps. Native stroke storage now
owns pointer history for pop/rollback, screen-to-world fit tolerance and endpoint closure.
Desktop defaults to pixel tolerance and near-start closure with explicit overrides;
camera changes preserve the gesture but disable automatic closure for that stroke.
Exact mesh projection versus Blender raster depth is documented as an intentional difference.

38 focused drawing/parity/architecture tests pass. Native build/3 CTests, drawing clang-tidy,
configured mypy (176 modules), Ruff and invisible D3D11 drawing acceptance pass. Actual image
tracing capture was inspected; repeated open/closed drawing, cancellation and one-action undo
also pass. Full development gate has not been rerun. Remaining release work listed above
still applies except these drawing sampling/closure details.

### Consumer density and desktop transport checkpoint

CurveUse density is now an optional override, inheriting the primitive's default (32 for
surfaces). Body pieces use independent counts; loft boundaries share the highest effective
request. One core sampling policy supplies construction, scheduling estimates and base-vertex
selection. The shared `consumer.sampling` operation enforces incoming topology locks, and
the primitive inspector exposes the override. Ordinary source edits remain independent.

39 focused primitive/shared-curve/surface/architecture tests pass. Full-QML offscreen checks
exercise actual numeric signals, matching base vertices, locked controls and unlocking.
This caught Qt transporting integral JavaScript values as doubles; the common desktop command
adapter now restores exact integers recursively, retaining strict core validation. Configured
mypy (177 modules) and Ruff pass. A complete gate remains pending after these changes.

### Full sampling gate and surface preview checkpoint

At c6e33d2 the full development gate passes: 822 pytest tests (9 existing Qt warnings),
3 native CTests, all native style, Python types/style/function limits, PowerShell checks,
numerical imports and native doctor. Log: `build/check-020-sampling.log`.

Closed-loft creation now has a separate owned mesh/alignment candidate, with Accept/Cancel
in Construction. Realign uses the same preview flow. A shared typed preview envelope owns
candidate lifetime and complete read validation for both surface and curve conversions.
Surface candidates are excluded from saves/history/picking, staged through existing mesh
publication, tracked in profiler ownership, and committed as one undo step on acceptance.
Metadata changes remain preserved; source/parent changes and deleted inputs reject acceptance.

22 focused preview/conversion/surface/architecture tests, mypy (179 modules) and Ruff pass.
Full-QML offscreen creation/realignment/acceptance and invisible D3D11 captures pass; inspected
`build/020-surface-preview/preview.png` shows the connected green closed-loop loft. Cancellation
releases preview viewport leases. These are offscreen checks, not interactive acceptance.
The full gate has not been rerun after preview integration. Authored fiber collision Issues,
broader anatomical/performance/resource qualification, examples/docs and packaging remain.

### Authored-fiber collision and Issues integration checkpoint

Native accepted-path checks now reuse the pinned addon collision kernels in one batched
world capture, without constructing a routing graph. They detect segment crossings and
closed-mesh containment, preserve expected bound-knot contacts, and never edit authored
engines or geometry. The ordinary read-only Issues coordinator captures owned resource
snapshots, cancels native work and rejects stale findings. GUI Issues lookup, labels and
navigation now use the shared object registry, including construction object renames.

23 focused collision/lifecycle/Issues/architecture tests pass, including cancellation while
saving and obstacle edits during a captured check. Native build/3 CTests, focused clang-tidy,
mypy (181 modules), Ruff and full-QML offscreen selection/frame/rename acceptance pass.
`build/020-fiber-collisions/collisions.afprofile.zip` attributes the native batched query.
The check describes accepted sampled centerlines, not continuous-curve or radius clearance.
No interactive desktop input or visible windows were used. The full gate and broader
anatomical routing/performance/resource/release qualification remain pending.

### Async creation invalidation checkpoint

A forced queued/running test reproduced silently lost surface/fiber creation when an input
changed. Jobs now declare whether input invalidation requests restart. The coordinator
retains the obsolete job until a safe terminal point, schedules its replacement before
reporting completion, and captures current inputs at dispatch. Explicit cancel, undo,
supersession and session close suppress restart; missing inputs report failure. This policy
is enabled only for authored surface/fiber creation, not previews or ordinary result jobs.

Fiber historical creation now shares accepted-result read validation with surface history.
Earlier snapshots receive pending construction when captured inputs belong to a later pose;
undo resolves their attachment field against the correct parent state. 19 focused creation,
history, fiber and architecture tests, mypy (181 modules) and Ruff pass. New tests include
queued/running input edits, cancel, undo/redo, deletion failure and historical pose validity.
Full development gate and the release work above remain pending.

### Full lifecycle gate and anatomical routing checkpoint

At 9bb0cbb the complete gate passes: 852 pytest tests (9 existing Qt warnings), 3 native
CTests, native style, Python types/style/function limits, PowerShell and native doctor.
Log: `build/check-020-lifecycle.log`.

Inspection found the warm-start adapter did not port the addon's per-span remapping. Six
donor cases reproduced differences up to 0.45 model units when anchors or sample counts
changed. Native warm continuation now resamples between corresponding authored pins;
all six match the actual addon solve within absolute 1e-10. No Python numerical work was
added. Compatibility also checks binding parent identities and closure.

Read-only background extraction from the original skull captured four evaluated SCPs
(9,158 vertices) and explicit endpoints from four saved BAKE paths. Fresh donor solves,
not those baked paths, provide expected outputs. All four cold/warm pairs match to 1e-10.
Source/file/Blender/addon hashes are pinned in the compact fixture. First native recorded
calls measured 18–44 ms; this is exploratory timing, not a repeatable performance claim.

The public API builds actual Fiber objects, previews/accepts routing conversion, removes
the independent source curves, creates a common-contract scalp loft and saves successfully.
Invisible D3D11 captures in `build/020-skull-scene` were inspected: paths follow the selected
skull context; the loft interpolates between them and can be occluded by the curved skull
(surface collision correction belongs to later volume work). 16 parity/architecture tests,
native build/3 CTests, warm clang-tidy, mypy and Ruff pass. Repeated profiling/resource trials,
remaining lifecycle review, documentation/examples and package qualification are next.

### Drawing depth and shared-construction qualification

Surface source insertion/removal/reordering now retains the existing density of unchanged
adjacent source pairs; new pairs use the configured strip count. A regression exercises all
three operations. 12 focused surface/workflow/architecture checks pass.

Pinned Blender source inspection and five failing tests identified target-before-substep
projection and first-event plane locking differences. The native adapter now uses the last
successful depth and precomputed target sample as Blender does, including a missed first ray.
43 drawing/parity/architecture tests, native build/3 CTests and drawing clang-tidy pass.
The invisible D3D11 drawing/tracing/conversion/undo workflow passes without QML warnings.

`tools/construction_profile_qualification.py` runs serial off/on/on/off trials over the skull
fixture with four shared loft consumers and 32 controller drag updates per trial. Mean work
including synchronous GPU readback was 15.01/20.20/22.75/19.17 ms; p95 was
18.29/29.06/30.99/21.26 ms. These are offscreen work intervals, not display latency or a
precise profiler perturbation estimate. System busy was about 14–17%; background activity
and thermal state were uncontrolled. Both recorded reports are complete without model resets.
Measured preparation maxima were 0.035 ms; publication 1.032/0.484 ms; viewport activation
1.545/1.698 ms. After settling, jobs/staging retained no geometry. Document/history ownership
overlaps and must not be summed. New Document followed by renderer draining released all
observed native geometry (zero bytes). Reports and measurements are under
`build/020-construction-profile`; the tool is maintained, generated reports are local evidence.
The skull paths-and-loft-only capture was also inspected, confirming a continuous surface.
No visible window or desktop input was used. Full final gate/package qualification is pending.

### Integrated offscreen and package preparation

Thirteen stable-content editor/renderer scripts pass: Construction, paths, images, Fiber,
routing, junctions, surfaces, closed preview, branch editing/rendering, consumer sampling,
and collision Issues. QML/controller checks use the offscreen platform; D3D11 texture checks
use an explicitly invisible QQuickRenderControl window. Forcing the offscreen platform on
D3D11 failed to initialize RHI; selecting the appropriate backend fixed the harness, not
production behavior. Logs are `build/020-<tool>.log`.

Saved-revision capture previously drained only mesh staging. It now drains mesh/path/image
models before final frames. A no-mesh/64-tile regression and a real CLI capture pass. The new
JSON example creates source curves, independent fibers, a loft and a synthetic embedded
reference grid. A 2048-square replacement remains renderable after its external source is
deleted; the saved image contains the expected pixels. These development transport checks
also load the complete QML application offscreen. Native portable execution remains pending.

The portable checker now follows first-class curve references and covers construction/image
workflow. Packaging includes Pillow codec notices, native routing provenance and PCG notices.
Active architecture/API/recommendation text is reconciled; `docs/construction_020.md` provides
the workflow and exact limitations. Ruff and focused architecture/capture tests pass.

### Source gate and ownership review

At 11dd5b8, `tools/check.ps1` passes: 869 tests (9 existing QQmlPropertyMap deprecation
warnings), 3 native CTests, all native style, Ruff, mypy on 181 modules, PowerShell checks,
locked dependencies, numerical imports and native doctor. Log: `build/check-020-candidate.log`.
The complete construction JSON example also runs in a fresh process without importing
PySide6, Shiboken or Blender. Origin/main remains at the original integration baseline.

Separate coordinator-authored ownership review traced registry, generic source consumption,
Fiber substitution, input capture/read validation, async creation restart, historical
publication, junction dependency aliases and resource reachability. New work extends the
existing coordinator, Issues and staged renderer; no parallel queue or Python numerical
fallback was introduced. Preview and displayed resources own leases independently. Numerical
branch assembly has explicit budgets and cancellation checks in sampled-grid/vertex work;
atomic upstream fitting retains its documented before/after cancellation boundary. Dense
authored identity traversal is still Python orchestration; measured costs do not establish a
current blocker or justify an unmeasured replacement. This is direct review, not an independent
agent review. Version metadata is advanced only for final candidate packaging; not yet released.

### Portable candidate progress

Candidate compiled source is ac19e77, version 0.2.0. The native versioned rebuild and
3 CTests pass. The Python wheel/sdist build and wheel resource check pass. Windows standalone
compilation is running (`build/package-020.log`); executable qualification is still pending.
Portable checks now include both a 64-tile embedded PNG and JPEG EXIF orientation. The JPEG
development transport check confirms rotated dimensions and preserved physical width.
Active documentation links resolve; remaining old schema-2 architecture text is corrected.

A bounded branch experiment used 4,096 samples on each main source and 254 branch roots.
Three runs with a timer requesting cancellation after 5 ms returned in 9.0–14.9 ms; one
observed cancellation and two completed before it was observed. Timer scheduling and
concurrent compilation prevent a precise cancellation-latency claim. The result supports
safe bounded completion for this fixture, not a universal responsiveness guarantee.

### Final contract correction: image alignment visibility

The final specification audit found that Face axis rotations did not implement the distinct
presentation setting for axis-only visibility. Added `only_axis_aligned` per workspace and
an actual inspector checkbox. Rendering and picking share one native batched local-Z/view-axis
predicate adapted from pinned Blender object.cc (source/hash in native provenance). Camera
direction is transient view state; changing it neither authors image placement nor schedules
geometry. Both projection types, all depth layers, reflected/scaled/sheared frames and current
view picking are covered. Appearance round-trips without affecting anatomical undo.

Native build/3 CTests, modified native style, mypy/Ruff, image and architecture tests pass.
The actual offscreen inspector checkbox and invisible D3D11 visibility/picking matrix pass.
The first ac19e77 executable finished building but is superseded before release qualification;
rebuild the candidate with this correction. The portable image test also checks the visibility
flag in an aligned capture and its disappearance after an oblique camera change. Final gate
and revised package qualification are pending. No visible window or desktop input was used.

### Revised gate and existing editing regressions

At c999896 the complete gate passes: **871 tests**, 9 existing Qt deprecation warnings,
3 native CTests, native/script style, Python types/style/function limits, numerical checks
and doctor (`build/check-020-final.log`). This is the revised portable candidate's runtime
source. Candidate compilation is in `build/package-020-final.log`.

Existing QA helpers still accessed embedded primitive curves. Updated current acceptance
fixtures to resolve first-class sources through their consumer references; the historical
0.1.5 alternative-evaluator experiment is explicitly labelled for its original revision.
Five additional source offscreen workflows pass: primitive/lattice/hook editing and reopen,
repeated insertion and snapped dragging, held-modifier camera/transform/offset gestures,
camera restoration, and a 512-SCP/128-point curve with inspector visible/hidden and undo.
Logs are `build/020-primitive-regression.log` and `build/020-*-final.log`. These are synthetic
events on the offscreen platform, not desktop input. QA helper changes pass Ruff and function
limits separately; no runtime source changed after the complete gate.
