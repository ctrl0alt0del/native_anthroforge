# AnthroForge architecture

The [0.2.0 specification](specification_020.md) and
[implementation plan](implementation_020.md) define the approved next boundaries:
first-class construction objects, referenced curves, Fiber as Curve subclass,
general surfaces, embedded images and schema 3 without older-schema migration.
See [implementation status](tasks/020-construction.md) for what is actually integrated.
Sections labelled with earlier release numbers describe their qualified baseline.

The confirmed specification remains authoritative. Imported meshes, lofts and curve-driven
bodies share the SCP document and evaluation lifecycle. Anatomical features enter through
the same core in later releases.

## Issue reporting (0.1.6)

Each Session owns an `IssueSystem`, separate from document/history state. Reporting,
listening, presentation and explicit resolution share a provider-scoped repository.
See [the addon-to-standalone component mapping and contracts](issues.md).
Checks are read-only jobs in the existing task coordinator; failed or cancelled
checks retain stale evidence. Repairs invoke shared application operations and must
pass a fresh verification. Document replacement and history navigation invalidate
check epochs. UI/JSON clients share `issues.*`; geometry diagnostics do not run in draw.
`RecordModel` supplies stable keyed Qt rows to both Activity and Issues. These
diagnostics do not certify unimplemented fiber, skin, collision or anatomy checks.

The [confirmed 0.1.2 specification](primitives_012.md) defines primitive and deformer behavior. Primitive
construction, deformers, shared controls and per-target bindings have separate
responsibilities. Authored parameters remain editable permanently; Apply/Bake is
excluded from UI and APIs.

## Ownership and execution

- core/document.py and entities.py hold immutable SCP records, UUID identities, canonical
  metre units, attachment bindings and named workspace state. A populated SCP hierarchy
  has exactly one root; an empty document is valid.
- application/session.py owns the current revision, immutable native mesh assets, history
  and scheduler. Commands are explicit and independent of viewport selection or Blender.
- application/commands.py is the shared UI/headless catalogue. Transactions collapse
  repeated drag updates into one undo step; cancellation restores authored state.
- application/coordinator.py owns dispatch, output reservations, coalescing, priorities,
  safe cancellation, publication and save checkpoints. Jobs acquire their input revision
  at dispatch. Queued writers also block commitment; read-only jobs do not.
- application/task_schedulers.py supplies dedicated attachment, import, project-open
  project-save, construction and control-attachment policies. Construction composes
  separate curve/body/loft, Hook, Lattice and Thickness stage estimates.
  Each assesses cheap metadata before admission and again
  before execution, returning an execution mode, estimated cost and coalescing delay.
  Policies share the coordinator's worker pool; they never start their own timers or
  publish results. Session.scheduler still names this coordinator for API compatibility.
- Each mesh asset owns a native handle. Workers retain snapshot mesh references; published
  geometry is immutable. Canonical polygon indices remain separate from render triangles.
- Native C++ handles import/triangulation, BVHs, exact picking, transforms and attachment
  calculations, curve evaluation, construction, Hook/Lattice and Simple Solidify.
  Numerical loops do not call Python per sample or iteration. Blender provenance and
  fixture limits are in native/migration/BLENDER_PRIMITIVES.md.

Python is an application-layer choice, not a Blender requirement. The original stack
decision retained it for command/authoring contracts, immutable document records,
scheduling policy, persistence and PySide adapters. Qt Quick also supports C++ models;
the headless API and AI integration do not intrinsically require Python. A full C++
application core is possible, but is a separate migration of those responsibilities.

The [native boundary audit](tasks/native-boundary-audit.md) checked current production
Python, native adapters and migration provenance. Influence inversion/membership,
display polyline/cage connectivity and cubic query preparation now run in native
batches. Default unit influence is represented by a null weight buffer. Component
editing groups world-to-local conversions by target frame, preserving selection order
and applying document commands only after all coordinate conversion succeeds.
Native callers retain buffer ownership through each call; nothing calls Python per
geometry sample or numerical iteration. Numerical algorithm ports must retain that rule.

Python still packs authored records/identities, applies document operations, validates
input and constructs Qt presentation records. Scalar UI arithmetic and fixed-size input
validation remain there. Those are not Blender algorithm fallbacks, but their allocation,
conversion and notification costs are real: eliminating Python numerical loops does not
establish a zero-overhead UI. Dense component presentation still materializes point
records and must be evaluated separately using actual GUI reports. The algorithms for
fibers, muscles, skin and warm-start fitting are not yet migrated into this release;
addon Python optimization loops must be ported in full when their features migrate.

## Construction and dependency boundaries

core/construction.py holds immutable Primitive, Curve, CurvePoint, BodyPiece, Control,
Target, Deformer and Thickness values. Shared controls own frames/cages; bindings own
membership, weights and settings. CURVE, BASE, GEOMETRY and LATTICE targets explicitly
identify the stage and optional owned component. Stable point IDs resolve to native
Bézier triple indices only when preparing evaluation. Lattice and mesh indices refer
to their canonical authored target, not a render triangle or temporary buffer.

core/results.py holds accepted geometry/control output and input revision provenance.
Authored SCP generations, construction revisions, pose revisions and accepted-result
revisions are distinct. entity_revisions.py classifies authored changes. A pose edit
does not cancel unrelated local geometry work. Attachment publication merges only pose
outputs into current state, preserving a newer primitive, result, name or color.

core/dependency_graph.py owns immutable output relationships: pose, control frame, cage
and geometry. application/dependencies.py owns traversal and job contracts over those
indexes. Jobs declare prerequisites and provided ports as well as complete object
writer reservations. A cage following its SCP pose is valid; feedback from that SCP's
surface is a real cycle. Cyclic/downstream outputs fail boundedly and retain accepted
data. Missing accepted surfaces fail instead of waiting indefinitely.

construction_evaluator.py prepares batched native pipelines from dispatch snapshots.
Control surface binding capture runs in the worker. Complete read sets are checked
before result adoption. Live consumers can use a Manual prerequisite's accepted result
with its revision and pending provenance; publishing that prerequisite triggers its
consumers. Preview/control movement is not an accepted surface.

Capture-only reads are declared separately from ordering prerequisites. A child's local
anchor is captured once; subsequent propagation does not depend on new child geometry.
Treating that capture as a permanent dependency would falsely cycle ordinary Hook/lattice
deformation. Geometry coordinates include the SCP geometry offset consistently in binding,
evaluation, component display and picking. Moving an origin rebases its following controls
to retain world placement and leaves the rendered geometry unchanged.
World-aligned viewport gizmos convert through control_frames.authored_frame before issuing
control.transform. Numeric fields continue to expose authored TRS in the documented frame;
the UI does not duplicate attachment/follow frame rules.

construction_policy.py and core construction validation own topology, references and
compatibility. Desktop controls expose those policies. Children and incoming surface
attachments lock topology; removing those dependents unlocks it. A follow reference
alone does not lock topology. Bindings are ordered within their actual target stage;
Simple Solidify follows generated-mesh deformation. Removal never bakes parameters.

construction_copy.py maps authored identities once across a copied subtree, preserving
internal sharing and independent copies. External support references remain explicit.
geometry_ownership.py traces current state, history, active snapshots and checkpoints;
render staging/display additionally lease native handles. Obsolete drag results are
collected rather than retained indefinitely in the asset catalogue.

## Attachments and history

Capture records a 28-double binding with parent triangle/weights, optional flow sample,
stable tangent hint, parent-frame offset and child-frame anchor/orientation. Direct child
edits retain the parent capture frame so an intervening queued parent edit cannot erase
the child edit. Publication checks relevant entity generations. Metadata edits retain
their newest name and colour while numerical results arrive.

The unchanged addon attachment-wave kernel performs propagation. Capture adapters preserve
triangle corner order and Blender's negative-scale decomposition; independent Blender
reference matrices test those choices. Failed dependencies become explicit failed SCP state.
No Python solver fallback is used.

Small Live attachment updates can execute through the coordinator on the calling
thread before a transform command returns, so the desktop publishes parent and child
poses in one event-loop turn. They use the same native evaluation and publication
validation as background work. The initial eligibility limits are 64 document entities,
64 capture candidates, 256 parent triangles involved in recapture, and an estimated
2 ms execution budget shared across a 16 ms window. Propagation of an existing binding
does not scan the parent mesh. These are conservative tuning values, not hard real-time
guarantees: synchronous work cannot be forcibly preempted. Measured overruns demote
subsequent similar requests to workers.

Larger interactive attachment requests use a delay derived from estimated work, between
16 and 100 ms. Replacements retain the first pending request's timestamp, including
when an edit invalidates its predecessor before submission. Coalescing cannot postpone
dispatch eligibility more than 100 ms; output reservations and worker availability can
add queue time. Explicit imports, opens, saves and recomputation have zero artificial
delay and remain background work. On Release and Manual activation rules are unchanged.

Estimates include whole-document ordering/packing and bounded metadata counts for
recapture; no mesh samples are evaluated during planning. Initial attachment costs are
heuristics. Up to 32 completed timing samples per workload-size bucket provide a
conservative measured estimate. File tasks begin with an unknown time estimate and
learn from matching size buckets; file metadata never makes file I/O eligible for inline
execution. Save estimation uses the selected immutable snapshot and its referenced assets.

Undo cancels jobs whose origin/start revision leaves history. Redo restarts their work;
it does not resume a paused solver. Historical entries share immutable data and retain
revision membership. Undo history itself is not persisted.

## Presentation and persistence

Qt owns its UI objects. RenderModel stages at most two 16,384-triangle chunks per tick.
QQuick3DGeometry owns its QByteArray buffers. Complete native meshes are prepared in workers;
the GUI retains the old complete mesh while preparing replacements. A frame boundary
activates the complete replacement; picking uses the displayed revision and retains its
handles until that frame is replaced. Superseded partial staging is discarded. Offscreen
capture advances the same publication protocol after completed GPU frames.
Hover, selection and visibility do not change authored mesh data. Mesh picking uses one
native scene call and per-mesh BVHs; no scene-level BVH yet. Component points and curve
segments use cached native AABB indices. Projection/inspector snapshots and geometry
notifications are separate from activity/status notifications.
Framing an empty group gathers its visible descendant meshes and asks the native scene
service for transformed bounds. It uses eight cached-bound corners per mesh, accounting
for rotation, reflection and geometry offsets without scanning every vertex on the UI thread.

Named workspaces preserve camera, orthographic mode, hidden/unpickable sets, member IDs and
independent overlays. Outside entities remain transparent/read-only while their dependencies
remain present. These presentation changes do not create anatomical undo steps.

Project schema 2 uses ZIP64 containers with JSON metadata and canonical NPY arrays
(allow_pickle=False). Saving writes a sibling temporary file, flushes it and atomically
replaces the target. A cooperative file lock prevents two writable application sessions.
Source and accepted meshes are embedded, with canonical triangulation retained through
deformation and reload. Native handles never serialize. Schema-1 meshes migrate to
imported definitions and accepted results; old applications reject schema 2. Loaded SCP attachments receive the addon's
equivalent startup synchronization; unrelated future solvers are not launched.

## Measurement and extension

Bounded samples record GUI ticks, frame intervals, picking, preparation, publication,
cancellation requests and safe completion. The Diagnostics overlay reports recent p95
values. tools/viewport_benchmark.py and tools/gui_acceptance.py record reproducible evidence.
Job inspection includes workload counts, estimated/actual cost, planned delay and execution
mode; Activity shows scheduling details when diagnostics are enabled. The scheduling
acceptance tool checks parent/child viewport-model poses at frame observations during
actual mouse drags. It does not claim to measure end-to-end input-to-photon latency.

JSON batch/line transports and numerical inspection run without Qt. Revision-matched image
capture starts Qt offscreen. The line server keeps scheduling while waiting for client input.
MCP, additional primitive families, fibres, muscles and skin remain separate feature migrations.

Qt/PySide versions must match when rebuilding the native viewport plugin. Windows DLL
preloading intentionally ensures Python and Qt use the same geometry registry. The current
portable package contains only dependencies needed by 0.1.5; numerical development extras
remain available for later migrations.

## Interaction and selection presentation (0.1.3)

`input_state.py` tracks physical held modifiers on the application window, including release,
auto-repeat suppression and window deactivation. `KeyboardManager.qml` owns semantic modifier
bindings and focus/modal policy; gesture consumers request insertion, surface snapping, extended
selection, precision, pan or deeper selection without knowing which modifier implements them.
Ctrl-click selection is resolved on release, allowing Ctrl to be held before a point drag.

`CurveEditor.qml` owns direct pointer gestures and transient preview lifetime; `curve_interaction.py`
adapts native cursor queries to `curve.split` and existing transform transactions. Cached world-space
cubics are rebuilt when authored geometry or its frame changes. C++ performs bounded closest-ray
queries and de Casteljau subdivision. Adjacent handles become Free to preserve the authored shape;
sampling resolution and stable references remain unchanged. Preview is never a document edit.

Surface snapping follows the addon's `core/scp_runtime/viewport_picker.py` contract: transform
the ray into mesh coordinates, raycast each eligible surface, and choose the nearest world hit.
The standalone's existing native batch scene/BVH queries already implement this numerical work.
Snapping uses displayed mesh revisions and their retained leases, excludes the edited SCP, and
allows visible read-only context as a target. It changes positions through shared point commands,
without adding an attachment. Complete gestures retain one undo transaction.

The viewport builds parallel orthographic rays and perspective rays from camera parameters.
Free translation uses the original pivot's camera depth. Editing geometry has a transparent
overlay pass with a shared camera projection, so outlines cannot hide component colors.
Curves, points and handles have distinct theme colors; point markers are native triangle buffers.
`PresentationCamera.qml` supplies the same camera to the outline and editing passes.

`KeyboardManager.qml` owns shortcut registration and context policy. Semantic commands
in the window reuse existing actions and the shared Delete dialog. Shortcut activation
is suppressed in modal/file dialogs and blocked saves; text fields retain editing keys,
and an active transform accepts explicitly declared view/transform/confirmation/cancellation
commands. No key event implements a core operation. Physical wheel/button capture belongs to
`InputState`; its semantic bindings and capture eligibility belong to the keyboard manager.

`TransformGizmo` owns gesture lifetime, `GizmoGeometry.js` owns projected handles/hit tests,
and `GizmoPaint.js` draws them. Projections refresh after frame synchronization, keyed by
camera, viewport, mode and transform. The Python transform adapter converts a complete
translation/angle/scale delta through native matrix operations and shared commands.
Object scaling remains local to avoid introducing shear into the existing TRS model;
world rotation is composed rather than added to Euler angles. Curve/cage transforms share
the same pivot/delta contract. Legacy axis-drag adapters remain compatible.

`ModalTransform` handles keyboard-started pointer transforms, using those same shared commands.
View changes recapture the current transform inputs without ending the original transaction.
Each gesture then resets its pointer reference in the new camera frame; stored cursor coordinates
are values, not live Qt property wrappers. Cancellation restores the original transaction snapshot.
Axis views center component selection or SCP bounds, retaining pixels per world unit at that depth.
The viewport captures a temporary camera value snapshot before the first axis alignment,
shared by keyboard and button paths. Further axis switches retain it; restore consumes it.
Position, Euler rotation, distance, projection and view label are restored through the same
gesture-rebase lifecycle as alignment. Workspace/document camera loading clears the snapshot.
Only the displayed camera uses existing workspace persistence; the return point is transient.
Modal rotation uses a native axis-angle adapter around the view direction. Selected curve points
include their handles during rotation/scale, while translation retains automatic handle behavior.

The transient curve interaction owns the signed snap offset. It reuses the displayed surface hit
and asks native code for its world normal, with inverse-transpose handling of nonuniform/mirrored
transforms. Wheel/reset events update the same active transform, not camera zoom or a second edit.
Offset and feedback clear on snapping release and gesture completion/cancellation.

`SelectionOutline` renders a depth-tested selection mask with the same cameras, displayed
mesh resources and active staging flags as the main view. A small screen-space dilation
shader extracts the silhouette at two logical pixels, including open surfaces and concavities.
Opaque context occludes it; X-ray excludes context occluders. Qt Shader Tools compiles the
shader into the native viewport plugin's resources during the existing CMake build.
The pass adds rendering work but no duplicate Python/native mesh conversion. Curve-edit
opacity and the mask never modify authored records or trigger construction calculations.

`application/deletion.py` owns single-SCP removal, root replacement, pose-preserving child
promotion, control detachment and rescheduling. It installs a valid hierarchy atomically
and retains existing history/checkpoint contracts. UI, keyboard and JSON clients call the
same `scp.delete`; shared-control deletion continues using `control.delete`.

## Runtime profiling (0.1.4)

`profiling/RuntimeProfiler` owns explicit recording, bounded immutable events and
atomic background export. It has no dependency on Qt, documents or task policy.
The desktop controller owns it across New/Open; headless sessions own a recorder by
default or borrow an explicitly supplied one. Session composes it with command/transaction
boundaries, task lifecycle adapters and
registered native calls. UI and API operations use the same runtime operations;
recording is never an authored revision or checkpoint-blocking job.
Closing a borrowing session detaches its native engine without stopping the recorder.
Replacing a task coordinator always reconnects the same runtime service.

`desktop/QtProfiler` is the C ABI adapter to `native/profiling`. The Qt 6.12.0 private
client runs on its own thread and enables only profiling services via a local socket.
Native input dispatch, model observers and render signals feed a bounded queue. No
Python callback executes on the render thread. Collection is inactive until requested;
only recording/export uses a Python polling worker and status timer. Qt engine support
is initialized dormant before engine creation and qualified separately for idle cost.

Stop freezes application spans, flushes the collector and streams the frozen ring to
an atomic report ZIP. Failed exports retain the ring for retry. Late task returns
cannot append to an exporting capture. Revision/job metadata connects work without
making the profiler a scheduler or geometry owner. Read sets, publication and undo
rules are unchanged. See [report limits and interpretation](profiling.md).

## Activity presentation (0.1.5)

`desktop/ActivityModel` owns a stable QAbstractListModel for the latest 40 jobs, newest
first. Its read-only `activity_rows` projection uses job fields without serializing
full scheduling workloads. Rows are keyed by job ID; insertion/removal/movement use
Qt model notifications and field changes emit only the affected roles. Completed
elapsed times stay fixed, and target-name updates preserve row identity.

The controller owns the model across document replacement and synchronizes it on the
GUI thread using the existing notification cadence. Active count/failure summary changes
are independent of row changes; diagnostic metrics have a separate signal. QML never
reverses/replaces the job list or scans it to compute header status. The coordinator,
headless job descriptions, cancellation/retry operations and checkpoints are unchanged.

This is a presentation adapter for existing job contracts, not a second task registry.
The profiler's generic Qt model collector observes incremental notifications without
Activity-specific timing instrumentation.

## Incremental evaluation and presentation

`core/DocumentIndex` belongs to an immutable snapshot. It holds read-only entity/control
lookups and a shared `Structure` containing validated authored identities, hierarchy order,
depths, forward/reverse dependency edges and blocked outputs. Value edits reuse structure;
reference, membership or attachment-policy changes revalidate it completely. Revision-only
replacement reuses the entire index. Indexes are runtime data, excluded from schema 2.

The application `ChangeJournal` retains 64 compact field-change descriptions, without
owning old documents. Desktop consumers have independent cursors; a missed interval or
document replacement requires a complete refresh. `SceneProjection` reuses scene rows,
parent choices and unchanged render projections. `PropertyProjection` owns stable,
read-only QML objects for authored records and updates individual fields. Curves and points
retain their QObject identities across coordinate edits; membership/order changes still
notify their collection. Published render leases and displayed-revision picking remain
owned by `RenderModel`, independently of these metadata projections.

Native geometry-only construction roots expose immutable vertices, canonical topology
and inexpensive bounds. Deformation, joins and Simple Solidify propagate this deferred
state. `af_mesh_finalize` first selects compatible accepted topology, then constructs
spatial acceleration and render chunks once. It returns a separate ready handle; published
meshes and cached bases are never mutated. Draft picking is rejected, and no lazy native
work runs during viewport adoption. Prepared C ABI entry points remain available.

Each `GeometryEngine` owns a locked Body base cache, bounded to 64 entries and 32 MiB
of native buffer storage plus a per-record allowance. Keys include sampling, shape,
sides, dimensions, length and closure. Fit/position and deformer settings operate later
on independent geometry. Eviction releases only the cache's ownership; workers retaining
a base remain valid. Session close clears the cache after workers stop.

`JobRegistry` separates active scheduling indexes from historical rows. Only active jobs
participate in tick, admission, dependency waiting, invalidation and checkpoints. Terminal
records retain output IDs, timing/assessment, state and actionable retry recipes; they
release execution callbacks, captured documents, futures and native cancellation handles.
Undo records a compact restart recipe before cancellation retires a job. Cancelled workers
can finish cleanup while transaction publication is blocked. Cleanup registers dependent
work before retirement, preserving continuous save blocking. History remains inspectable;
the Activity panel's 40-row limit does not truncate application history.

## Workflow inspection and presentation

The dependency structure caches strongly connected components alongside reverse edges
and blocked outputs. Shared inspection queries label true cycle members and downstream
causes, expose attachment frames through existing batched native queries, and report
topology restrictions from their existing application policy. The desktop inspector is
opt-in and revision-gated; it reuses field-level property projection.

Workspace policies own mixed SCP/control membership and reference validation. Deleted
references remain valid presentation history for undo; new unknown references are
rejected. Category visibility/pickability are shared policies. Desktop projections apply
them to displayed geometry and cached native component indexes; pointer movement does
not introduce Python geometry scans. Numeric/vector adapters convert dimensional fields
at the UI boundary; canonical geometry and headless operations remain in metres.

Inspection export freezes document/geometry ownership and presentation at invocation.
Its read-only job uses the existing coordinator and a dedicated background scheduling
policy. Metadata generation, temporary project encoding, isolated GPU rendering and atomic
archive publication run outside the GUI thread. The child renderer disables its scheduler
timer and uses explicit saved-revision inputs; observed camera/selection are verified.
Job retirement releases snapshot assets; temporary files and processes have bounded,
cancellable owners. Export failure cannot replace a previous report. The headless core
does not import Qt; JSON-only inspection has no renderer dependency.

## Measurement evidence and recording-only resource observation

Workspace-owned immutable surface witnesses retain source identity, accepted revision,
frame and captured world coordinates. Native queries resolve barycentric positions and
Euclidean distances. The desktop shares existing displayed-revision picking and leases;
staging retains the visible geometry's provenance. Shared application operations own
annotation validation/persistence, while the viewport owns transient hover and gesture
rebasing. Frozen reports consume the same query contract. Camera bookmarks and rulers
remain outside anatomical undo and do not retain native mesh handles.

The runtime profiler observes changes at the ChangeJournal/coordinator boundaries and
cache policy at the engine-owned base cache. Its resource collector owns only weak
references, installed while recording. Native registry snapshots return bounded handle,
allocation-identity and capacity metadata without copying geometry. Owner traversal stays
on the session thread; job observation is synchronized and bounded. Rendering contributes
displayed/staged native leases through a weak adapter callback. Alias identities are
deduplicated before export; raw allocation addresses are not serialized. Owner totals
overlap and unobserved/transient or non-native allocations are explicitly outside coverage.
Recording off performs no new inventory queries, traversal or cache event collection.
