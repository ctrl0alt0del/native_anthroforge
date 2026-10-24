# AnthroForge architecture

See the [current addon functionality audit](addon_functionality_audit.md) for implemented
families and missing authoring details, and [known parity findings](addon_parity_findings.md)
for source-frame, effective-policy and child-anchor fidelity defects. The distinction
between a supported operation and faithful migration must remain explicit.

## Planned 0.3.5 mirroring — not implemented

The [confirmed contract](specification_035.md) and [implementation plan](implementation_035.md)
introduce source/rule spatial instances at the typed-reference and surface-provider
boundaries, not additional authored hierarchy nodes. Every stage is a strict reflection
of the corresponding source output; independent mirrored solvers and stacking are forbidden.
Shared controls/resources retain their identity and ownership. Instance-aware attachment
findings do not deform reflected geometry. The existing coordinator and staged viewport
must preserve source/mirror revision agreement, accepted-input provenance and resource leases.
Desktop and headless use the same read-only capabilities and removal policies. These
paragraphs describe planned architecture, not available operations or measured acceptance.

## 0.3.3 observation and scheduling costs

The desktop property-query service owns bounded metadata caching and per-object QML
epochs. Shared property adapters remain authoritative for edit restrictions; value
bindings remain independent. Session-owned formula invalidation indexes conservative
read candidates, retaining exact input checks and full structural invalidation. The
active job registry owns prerequisite links; ranking and temporary urgency donation
consume those links without changing scheduling policy. Immutable publication avoids
an unnecessary second document construction when edit contexts are unchanged.
See [measurements and preservation evidence](shortcuts_033.md) and CH-070.

## 0.3.2 comparison and evidence ownership

The session comparison service owns one accepted baseline, independent resource catalogue,
and bounded semantic journal. Existing read-only coordinator jobs own frozen comparison
and export inputs. Native fingerprints detect changes without defining attachment or vertex
correspondence. Historical viewport models stage their own leases and never enter picking
or snapping. Feedback drafts freeze evidence before their modal opens, and the generic
consumer contract streams owned file attachments. Replay validates its archive and runs
only whitelisted operations in an isolated session, preserving the active session and user
preferences. See [the feature contract](shortcuts_032.md) and CH-069.

## 0.3 shortcut and Parametric boundaries

Migration extensions retain Bézier knot metadata under native Parametric evaluation;
interpolation and segment sampling belong to the engine definition. The application
validates compatible topology before atomically switching definitions. Attachment
policy scope is a separate validated reference from inferred shortcut ownership.

`formula_batches` partitions expression work where it crosses an evaluated pose/path/
geometry output; a formula worker cannot calculate those intermediate outputs itself.
Coherent property groups stay together. The existing coordinator schedules each batch,
captures dispatch state and rejects stale publications. No second executor is introduced.
Immutable document snapshots retain formula lookup indexes across result-only publication.
Effective shortcut policy reads also participate in pose batch planning, so temporary
Surface Nearest overrides cannot create artificial waits inside a joint pose batch.

The [confirmed shortcut/Parametric contract](specification_030.md) and
[implementation plan](implementation_030.md) govern this extension. Lower-level
numerical properties remain independent of shortcut wrappers. A property catalogue maps
stable references to existing semantic edit operations; wrappers own exposure and optional
attachment-edit policy. Direct property editing does not activate wrapper policy, while
shared validation still protects driven, read-only and topology-locked targets.

Shortcut edit contexts also retain existing bindings for controlled SCP transform
properties before writes. Attachment evaluation composes temporary overrides over
those bindings, then resolves them without recapture. Default retention is ready
immediately and uses no extra preparation job. Context ownership already spans delayed
formula publication, update modes, history and persistence; direct property edits and
explicit rebinding supersede it. Retention does not imply optional owner backsolve or
assign a policy scope to multi-owner drivers (CH-067).

Driving ownership is inferred from controlled properties, chains and shared construction.
Only the initiating wrapper contributes temporary attachment policies. The current graph
and coordinator own formula outputs, coupled validation, accepted-value provenance
and gesture contexts; no second scheduler or recursive user-edit publication is introduced.
Native compiled expressions are shared by drivers and Parametric sampling, with numerical
types/units and the language restricted by AnthroForge rather than library defaults.

Curve authoring is engine-specific: formula definitions and generated points
cannot be treated as independent authored Bézier controls. Stored definitions, generated
identities, post-formula deformation, resolution locks for junctions and generated-point references, and exact independent
Fiber conversion are distinct responsibilities. Schema 5 includes schema-4 loading
for 0.2.4 projects without blanket recomputation. Native expression qualification and actual old-executable
compatibility checks are recorded in the [implementation review](research/shortcuts_030/windows_review.md).
Generated-point resolution policy is shared by direct, wrapper, formula and engine-switch
writes; property inspection presents the same reason in desktop editors. The canonical
0.3.0 package passes the portable checks, including native hidden rendering.

## Current architecture

The 0.2.4 VCP performance work preserves document, numerical and attachment contracts.
`TissueInspectionTools.state` exposes prepared field-level presentation through the
existing projection layer. Accepted-result provenance indexes pending owners once;
typed local TissueVCP strategy edits reuse relationship validation while still running
the full tissue capability policy. Other record/reference changes invalidate that reuse.

Native advisory collision checking owns an exclusive retained context with immutable
collider snapshots and revision-qualified pair evidence. It is bounded to 128 MiB;
changed geometry, transforms, contacts, ordering and metric tolerance invalidate the
affected evidence. Stacking uses exclusive multi-call leases across planning, solving,
group validation and inspection. Idle sessions are bounded to four/512 MiB and cannot
return across a lifecycle clear. Native signatures still qualify every captured input.

`tissue_preparation` owns immutable accepted-base vectors, Section Profile frames and
Distributed mass/cotangent operators. Its engine LRU charges source retention as well
as preparation (64 MiB/64 entries). Per-call solvers remain independent; changed
Distributed distance refactors the numerical matrix. Internal envelope sides use
existing draft meshes; accepted composed stages retain complete rendering/query data.
Height smoothing eliminates pinned variables and uses PIQP box bounds, then expands
primal/dual results for the original full-problem optimality certification.

Profiler resource observation remembers weak immutable catalogue groups rather than
expanding every shared payload repeatedly. Inventory expansion stays bounded and runs
only while recording. Cache ownership and hits/misses remain visible in reports;
opaque stacking cache storage is explicitly labelled as a conservative upper bound.
See computation records CH-039 through CH-044 for measurements and limits.

[0.2.3 preferences](specification_023.md) live in application-owned `PreferenceStore`,
separate from project/history state. Desktop and headless commands share atomic
persistence. Path jobs and conversion previews capture immutable preferences at dispatch
and pass the backend through the native ABI. Each native SQP job owns its candidate
strategy/context; sparse PIQP preparation/solving belongs to `routing_qp_problem.cpp`
and `routing_piqp.cpp`. Outer routing remains shared. Accepted path diagnostics retain
backend provenance; old schema-4 results without this field identify Custom.

The [0.2.2 specification](specification_022.md) and [implementation plan](implementation_022.md)
define the implemented unified TissueVCP, Point/Anchor and Surface/Membrane extension,
shared surface providers and schema 4. [Validation](development_status.md#unified-tissues-022)
records current evidence; sections labelled with earlier versions preserve their history.

The [computation inventory and history](computation_history.md) maps current numerical
and supporting workloads to their owners/tests and records changes of approach,
observed causes, replacements, evidence and limitations. Update it with computational
changes; this architecture document remains the description of current boundaries.

Distributed muscle direction construction belongs to `native/src/tissue_directions.cpp`.
It uses an owned material mesh and physical mass/stiffness operators; no numerical
work or callbacks move into Python. The pinned addon kernels remain unchanged.
`smoothing_core.cpp` adapts their field preparation and QP for standalone publication,
while the shared `mesh_quality` boundary owns complete-mesh deformation acceptance.
Inflation, smoothing and relaxation use its tissue acceptance policy: finite output
and no new collapsed faces, with self-intersections allowed. Its separate diagnostic
plane-side predicate still distinguishes transverse crossings from coincident shell
boundary contact; strict diagnostic validation remains available without governing
tissue publication. Relaxation acceptance is native so direct and application callers
share the same rule. Refinement
subdivides existing material intervals instead of overlaying a second uniform grid.
Document settings, topology correspondence, scheduling and publication contracts remain
unchanged; the [repair record](tasks/muscle-height-smoothing.md) tracks qualification.

The surface-provider boundary retains bind-time geometry for Anchor
attachments. C++ resolves referenced material coordinates against the current accepted
surface into a geometry-only lease with the captured index layout. The shared attachment
kernel then resolves its unchanged frame/offset record. Canonical polygons and tissue-side
correspondence survive envelope compaction. Accepted crop provenance retains the base
that defined the material cut, so anatomical deformation does not clip away bindings.
Explicit plane edits redefine the cut; material removed by an explicit topology edit
still fails without reassignment. This lease is never a display/picking surface. Captured resource IDs are
serialized and included in document/history/job ownership. Fiber fields now use typed
surface-role/material captures too. Multiple captures can reference the same provider:
native field assembly retains unedited structural pins on their original capture while
new influences capture current real geometry. Target-relative regions retain an owned
batch of material bindings against inflated rest vertices. Native resolution applies the
captured target frame and normal offset in tissue-local coordinates; it does not rewrite
shared sources. Rest-topology changes require explicit rebind or unlink.

Asynchronous authored capture publication validates its read set against each affected
history entry. A capture from a later parent pose cannot populate an earlier entry:
that entry retains the capture request and runs it against its own inputs when revisited.
Every execution owns separate immutable resources, including history/redo captures.
This policy is shared by Anchor, Fiber and tissue-region creation/rebinding.

Accepted surface meshes retain structural material pins from their accepted Curve/Fiber
inputs. Native capture maps authored parameters to material chart coordinates (or exact
patch barycentric rows); source refinement and ordinary transforms preserve this metadata.
Stacking preparation resolves it to sparse exact displacement equations, retaining cropped
hidden variables. It does not pin every contributing vertex. Schema-4 resource storage,
history/checkpoints and native memory accounting own these records with the mesh. Point
protection is separate from curve shape, so changing it never silently recaptures bindings.

Tissue stacking separates native candidate/order planning from final evaluation. Candidate
geometry is observed without declaring every nearby tissue a prerequisite; accepted plans
install only actual provider-final dependencies. Complete read sets are validated at
publication. A read conflict retires the job as obsolete and retries through the existing
coordinator, rather than reporting a numerical failure. Frozen provider results retain
their matching material/settings snapshots, including Manual provenance. Identical final
geometry reuses its native resource and content revision to prevent publication feedback.
Explicit/excluded pair intent and selected material regions persist separately from order
evidence. The focused desktop inspector uses the shared operations. Whole-tissue strongly
connected stacking orders use one atomic final bundle: C++ solves the actual side graph
using each receiver's settings, while ordinary source/attachment dependencies remain intact.
The coordinator owns all selected output reservations and complete read validation; Manual
members supply retained accepted output until requested. Complete assembled shells/envelopes
undergo independent fold, bone and neighbor checks before publication. Crossings within
one tissue are permitted by the October 21 policy; distinct tissues remain separate.

Confirmed placement owns a transient exterior query through `application/surface_queries`
and the native CGAL/libigl adapter. Native qualification checks unique/nondegenerate
topology, intersections, ambient-cell exposure, orientation and complete original-face
correspondence against the same temporarily closed input. Eligible queries retain the
original immutable mesh and its acceleration structure; other inputs use full cleanup.
Exact intersection arrangement and ambient-cell
extraction exclude buried/sealed-cavity fragments; accepted material bases temporarily
close open tissue, with added closure excluded from selection. Original triangle
provenance is retained for attachment capture and subsequent deformation. The native
cache owns its resources within 64 MiB/64 entries; document/history contain originals.
Scoped native storage accounting includes prepared buffers/tree/render storage and
deduplicates shared allocations within a query. Live leases survive cache eviction.
Preview remains raw and responsive. Completed curve/point/drawing gestures run query
preparation in coordinator workers and merge into their initiating undo step. Newer
authored edits supersede pending placement; Undo can recover the earlier request.

Ambiguous stacking uses a separate native BVH query along geometric base normals,
choosing the farthest distinct positive hit. It changes support correspondence only
where multiple hits exist; vector transport, localized constrained solving, exact
attachments and unambiguous donor behavior remain. Cache versions include this policy.

Routing derives obstacle roles from dependency ports and sends the accepted provider
geometry to the existing native collision world. Empty accepted outputs remain dependencies
but are filtered before collider indexing. Automatic source-consumer cycles are excluded;
explicit cycles remain errors. Advisory collision queries isolate unavailable providers,
retain other findings and report the incomplete surface check without role substitution.

The [0.2.0 specification](specification_020.md) and
[implementation plan](implementation_020.md) introduced the construction boundaries:
first-class construction objects, referenced curves, Fiber as Curve subclass,
general surfaces, embedded images and schema 3 without older-schema migration.
Schema 4 replaces that storage format in 0.2.2; earlier formats are rejected.
See [implementation status](tasks/020-construction.md) for what is actually integrated.
Sections labelled with earlier release numbers describe their qualified baseline.

The confirmed specification remains authoritative. Imported meshes, lofts and curve-driven
bodies share the SCP document and evaluation lifecycle. Anatomical features enter through
the same core; unified tissue VCPs use it in 0.2.2. The
[0.2.1 contract](specification_021.md) adds the curve-workflow boundaries below.

## Automatic routing and optional editors (0.2.1)

`core/routing_obstacles.py` owns eligibility and automatic dependency edges. Its SCC pass
removes only automatically introduced cyclic geometry edges; explicit cycles remain errors.
The graph captures a structural scene signature, used by a `routing_scope` read revision.
Scene membership changes invalidate jobs/previews even when a provider was absent from the
previous capture. Surface pose/geometry reads remain conservative across the complete scene.
`dependent_tasks` marks geometry pending before fan-out to controls, paths and mesh jobs;
Manual shape changes therefore remain visible in consumer provenance without changing queues.

Native routing captures immutable collision worlds under independent shared-pointer leases.
The engine caches them by mesh handles, exact transforms and clearance through `ResourceCache`
(64 MiB, eight scenes). Solves retain their own leases across eviction, use native BVH queries,
and validate against the full eligible scene. No straight-segment-only obstacle pruning or
Python geometry loop is introduced. Capture and solve have separate profiled ABI boundaries;
cache events and observed native capture capacities join overlapping resource inventories.

`ChoiceModel` composes keyed `RecordModel` rows with a Qt sort/filter proxy. Both optional
editors use the same bounded virtualized QML component and filtered bulk semantics. Routing
descriptions cache structural inputs; result publication does not rebuild the candidate graph.
`core/curve_constraints.py` supplies required-point reasons to both API validation and UI.
The keyboard manager owns the continue-placement modifier; `DrawingTools` owns provisional
points, finalization and coherent undo. No document mode or calculation policy lives in QML.

## Issue reporting (0.1.6)

Each Session owns an `IssueSystem`, separate from document/history state. Reporting,
listening, presentation and explicit resolution share a provider-scoped repository.
See [the addon-to-standalone component mapping and contracts](issues.md).
Checks are read-only jobs in the existing task coordinator; failed or cancelled
checks retain stale evidence. Repairs invoke shared application operations and must
pass a fresh verification. Document replacement and history navigation invalidate
check epochs. UI/JSON clients share `issues.*`; geometry diagnostics do not run in draw.
`RecordModel` supplies stable keyed Qt rows to both Activity and Issues. These
diagnostics do not certify anatomical correctness or unimplemented skin/volume checks.
Authored fiber centerline collisions are read-only native checks over accepted geometry.

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
  project-save, construction and control-pose policies. Construction composes
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
records and must be evaluated separately using actual GUI reports. Curve drawing/fitting,
Fiber deformation, routing preparation/solving/warm remapping, and surface construction
now run in C++. Muscles and skin remain later work; their numerical loops must follow
the same native-only boundary when they migrate.

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
Anatomical binding capture runs in the worker for SCPs and fibers. Controls use ordinary
transform following only. Complete read sets are checked
before result adoption. Live consumers can use a Manual prerequisite's accepted result
with its revision and pending provenance; publishing that prerequisite triggers its
consumers. Preview/control movement is not an accepted surface.

Capture-only reads are declared separately from ordering prerequisites. A child's local
anchor is captured once; subsequent propagation does not depend on new child geometry.
Treating that capture as a permanent dependency would falsely cycle anatomical
deformation. Geometry coordinates include the SCP geometry offset consistently in binding,
evaluation, component display and picking. Moving an origin rebases its following controls
to retain world placement and leaves the rendered geometry unchanged.
World-aligned viewport gizmos convert through control_frames.authored_frame before issuing
control.transform. Numeric fields continue to expose authored TRS in the documented frame;
the UI does not duplicate follow frame rules. In 0.2.0 controls use only ordinary
transform following. `object_frames.Frames` resolves generic object transforms with
one cycle guard; geometry offsets remain geometry-space data. Origin relocation
rebases ordinary children and live consumer placement atomically. Controls live in
the Construction projection, while the anatomical outliner contains only anatomy.

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

`fiber_supports.py` owns dense deformation candidate policy for Fiber creation and
current-shape editing. Endpoint selection remains separate: skeletal fibers can
use nearby eligible SCPs; explicitly tissue-backed fields use selected parents.
Unrelated tissue proximity does not introduce an anatomical dependency. Native
capture/blending remains batched and retained material bindings remain authoritative.

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

Project schema 3 uses ZIP64 containers with JSON metadata and canonical NPY arrays
(allow_pickle=False). Saving writes a sibling temporary file, flushes it and atomically
replaces the target. A cooperative file lock prevents two writable application sessions.
Source/accepted geometry, paths, attachment fields and deduplicated image bytes are embedded.
Canonical triangulation survives deformation and reload. Native handles never serialize.
Unsupported older schemas are rejected clearly. The 0.1.x schema-1 migration belongs to
that historical release, not the current loader. Loaded SCP attachments receive equivalent
startup synchronization; unrelated solvers are not launched and paths do not blanket-reroute.

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

The transient curve interaction owns the nonnegative snap offset. It reuses the displayed surface hit
and asks the shared native `surface_snap` helper for outward placement, with inverse-transpose
handling of nonuniform/mirrored transforms and a scale-aware numerical margin. Native drawing,
point placement and cursor placement use the same policy. Exact picking and measurement hits
retain their unshifted coordinates. Wheel/reset events update the same active transform, not camera zoom or a second edit.
Offset and feedback clear on snapping release and gesture completion/cancellation.

`UiNumberField` owns decimal parsing, integer policy, display formatting and horizontal
scrubbing; scalar, vector and anatomical-transform controls all use it. Dot and comma
decimal separators are accepted independently of the OS locale; thousands separators
are not accepted. `NumericEdits` owns a scrub's existing application transaction, including
rollback on cancellation, lost window activation, destroyed controls or command failure.
Domain values update through the same commands as typed edits and commit as one undo step.
Draft tool settings and workspace-only values use release-only publication, without
pretending to participate in document undo. KeyboardManager retains shortcut ownership.

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
replacement reuses the entire index. Indexes are runtime data, excluded from project files.

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

`TaskPriorities` owns queue rank independently of per-task execution/delay hints.
Publication and automatic retry carry causal interactive urgency and original request
age; replacements and coalescing retain their first pending queue age too. Destination
workspace priority remains its own. Active consumers temporarily donate their full rank
to transitive prerequisite jobs. Ranking is recomputed from active port indexes, so
finished/cancelled consumers cannot leave stale boosts. A borrowed boost is not inherited
by unrelated work created during publication. Equal rank uses causal age, original queue
age and creation order, avoiding replacement starvation. Jobs still pass existing readiness,
exclusive-writer, dispatch capture and publication checks; workers are not preempted.
There are no anatomy IDs, task-kind exceptions or global anatomy-before-tissue barriers.
The profiler records requested/effective demand and its donor, plus prioritization cost.

## Workflow inspection and presentation

The dependency structure caches strongly connected components alongside reverse edges
and blocked outputs. Shared inspection queries label true cycle members and downstream
causes, expose attachment frames through existing batched native queries, and report
topology restrictions from their existing application policy. The desktop inspector is
opt-in and revision-gated; it reuses field-level property projection.

Workspace policies own anatomical membership, construction association and reference validation. Deleted
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

## Construction image ownership and presentation (0.2.0)

`authored_jobs` owns the common initiating-history-step publication used by mesh and
image imports. Image jobs decode PNG/JPEG and apply EXIF orientation off-thread, then
prepare native 256-pixel RGBA tiles. Assignments own physical dimensions and ordinary
parent-local transforms; assets own source bytes and decoded/native image storage.
Multiple instances share one asset. History/checkpoints/jobs and viewport leases preserve
that asset until their last owner releases it. Native plane queries and calibration share
top-left normalized UV coordinates and full affine frames.

Workspace `ImagePresentation` records own opacity, depth, sides, projection visibility and
pickability. These changes do not author geometry or trigger calculation. Displayed-content
records preserve old dimensions and provenance during replacement. The shared staged model
filters content into Qt render layers; each layer creates only its own tile delegates.
Native image geometry transforms six vertices per tile, retaining affine shear. Texture
data is unchanged during transforms. Picking follows displayed content and the current
viewport projection rather than the delayed saved camera settings.

Texture-only experiments found instanced custom image quads invisible on this D3D11 setup;
adding normals/index buffers did not resolve it, whereas native-transformed non-instanced
quads rendered correctly. Dynamic reparenting between Qt View3D scenes also lost display.
The maintained implementation uses transformed quads and staged layer models, with tests
for orientation, occlusion and complete replacement. These are scoped observed results,
not a claim about every Qt backend. No visible-window acceptance has been performed.

## Curve surface ownership (0.2.0)

`core.curve_consumption` defines primitive/surface source references. The shared application
consumer policies own transforms, independence and reference rebasing across reparenting,
deletion and origin relocation. Surfaces own correspondence, density and range settings;
the source remains an independent authored curve or Fiber. Closed correspondence stores
authored point identity plus a segment fraction, and changes only on explicit Realign.

Creation/Realign uses the existing asynchronous authored-job boundary. Subsequent geometry
uses `construction_tasks`, with a surface workload strategy and generic geometry result
publication. Native loft/patch work returns complete finalized meshes. Construction
projection sends these to the same staged mesh model and displayed-revision picking used
by SCPs, while excluding them from anatomical snapping/attachment candidates. Issues use
generic object scopes and the shared evaluation operation. Explicit junctions supply shared
source identities to branch assembly; no proximity welding or separate Fiber loft exists.

## Curve engines, bindings and construction lifetime (0.2.0)

The object registry provides generic identities and poses without substituting construction
ownership for ordinary parenting or anatomical attachment. A Fiber subclasses Curve; its
bindings resolve current shape before the same engine interface evaluates it. No public
Free/Controlled or solver-generation hierarchy exists. Engine-specific settings are typed.
`curve.engine` preserves resolved authored points and installs the selected engine through
the common edit/revision/dependency pipeline, with one undo action. The desktop selector
dispatches only on user activation; state refreshes and undo do not author edits. Existing
coordinator policies own evaluation, cancellation and failure retention. Optional resampling
conversion has a separate read-only preview/acceptance API; ordinary selection does not use it.

Junction output ports distinguish canonical source publication from followers' path outputs.
Atomic authored edits update incident points together; the dependency graph retains accepted
Manual prerequisites and detects genuine cycles. Surface consumers own correspondence and
sampling, including persistent closed alignment and per-pair density. Primitive consumers
use the same source-reference and placement policies.

Authored creation jobs opt into input-invalidation restart through an explicit Job contract.
The coordinator waits for safe termination, registers replacement work before reporting the
old job terminal, and captures fresh inputs at dispatch. Explicit cancellation and history
navigation suppress that restart. Historical result adoption validates the complete read set;
an older document cannot inherit geometry evaluated against a newer pose.

Resources retain mesh/path/image/attachment allocations across current state, undo/checkpoints,
workers and displayed/staged leases. Profiler observation is read-only and recording-only.
Saved-revision rendering drains all staged resource models before capture. Schema 3 persists
owned editable state and accepted results, never native handles, undo history or preview data.

## Adaptive surface material correspondence

Exact surfaces retain normalized longitudinal stations independently of vertex indices.
Accepted tissue results own their source coordinate basis, including part charts, periodic
axes and patch projected positions/perimeter coordinates. This metadata survives deformation,
crops, envelope composition, snapshots and serialization and is included in memory accounting.
It contains no live source handles.

`surface_providers.binding_frames` is the shared boundary for Anchors, Fiber influence
fields and tissue target-region goals. Native material queries resolve captured locations
on current triangles and transport the captured frame/offset without recapturing them.
Ordinary unchanged-domain captures use the existing canonical mapping. Sampling changes
use material-space acceleration, cancellation and explicit coverage validation; missing
material remains a failure. Authored topology policies remain separate from this numerical
correspondence. Indexed authored fields and selected-face masks retain their existing
topology restrictions.

Patch transport uses signed mean-value coordinates on matched perimeter stations, including
both boundaries' corners. It preserves linear precision when only sampling changes; it does
not remesh or move the patch itself. At shared rim/sheet edges the native spatial lookup
selects the material plane compatible with the retained frame.

## User feedback reports

The [feedback reporting subsystem](feedback_reports.md) is separate from anatomical Issues,
inspection exports and profiling. Immutable Qt-independent report records cross a small
consumer boundary; the local consumer owns atomic, idempotent archive publication in a
version-independent user inbox. A receipt describes where to reveal the result, allowing
file or online destinations without changing the editor. The service owns one background
submission and explicit failure/retry; it does not enter document scheduling or history.
Desktop capture precedes the modal. One QPainter adapter draws source-pixel annotations
for both the fitted/zoomed preview and worker-side PNG export.

The separately injected `feedback.inbox.ReportInbox` capability owns listing, reading,
description edits and deletion; submit-only destinations retain their narrow consumer
contract. The local adapter uses bounded archive reads and atomic description replacement.
`desktop.report_browser` runs on-demand I/O/preview decoding on its own worker and exposes
a keyed model plus a single owned image. It has no idle work and never enters document
history. Failed edits retain the UI draft; deletion requires explicit confirmation.
Both desktop adapters use the same version-independent inbox in the composition root.

## Fiber interaction capabilities

`application.transform_policy` owns direct object-transform eligibility. The object
command enforces it and desktop selection projects it separately from workspace
read-only state. Component editing supplies its own transform target. Keyboard bindings
declare capabilities; toolbar, gizmo, modal transforms and numeric fields consume the
same eligibility instead of testing object names or kinds in QML.

`desktop.creation_selection` follows a declared primary object of an authored creation job through
publication, including replacement jobs for changed inputs. It consumes the selection
intent once, exits component editing and selects the accepted output. Document/session,
workspace, selection, edit-mode and undo-epoch changes invalidate the intent. It never
publishes geometry or changes scheduling/history; failure/cancellation leaves editing
context intact. Viewport toolbar containers consume unused pointer events so disabled
controls cannot accidentally select geometry behind them.

## Attached construction creation and transient feedback

`core.tissue_creation` separates creation eligibility from the strict evaluator contract:
Tissue sources remain Anchor/Fiber/Membrane. `application.attached_creation` plans an
independent required source graph for `membrane.create` and generic `tissue.create`.
The existing coordinator reserves all new object IDs. Owned worker snapshots use native
binding capture and surface evaluation; one publication installs the graph and its resources
into the initiating history action. Downstream tissue jobs are registered before creation
finishes. `attachment_defaults` owns nearest-SCP policy for Points and Fibers. Internal
junctions and existing Fiber bindings are retained by shared copy infrastructure.

`UiNotice` is nonvisual feedback, delivered to a bounded `ToastBus` and bottom-right
`ToastOverlay`. It cannot affect layouts or take input focus. Persistent details remain
in their existing models; no document, scheduler or undo state belongs to the toast.
Scroll views reserve a scrollbar gutter and changing detail values elide in stable rows.

## Publication barriers (0.2.2)

Accepted-output notifications traverse aliases to the next registered evaluator, then stop.
That evaluator's publication controls further propagation. This lets unchanged final tissue
geometry suppress downstream work even when candidate plans change. Authored invalidation
remains transitive; failure publications notify consumers through the same boundary. Candidate
observations remain separate from anatomical prerequisites. Tests cover creating supported
fibers after their tissue support exists, which previously caused a plan/path feedback loop.

## Branched construction interaction

`DrawingTools` owns the provisional placement lifecycle. `BranchPlacement` captures
authored controls from displayed path resources and caches owned coordinates in the native
component index. Perspective/orthographic closest-point projection is native; no Python
per-control scan runs on pointer motion. The first click seeds an owned native stroke.
`curve.branch.create` validates and publishes the new curve plus explicit junction as one
shared application edit, reusing canonical junction ownership and normal path scheduling.

`surface_grouping` resolves semantic source groups from explicit junction identities before
existing asynchronous surface construction. It never changes numerical loft/branch assembly.
Group partitions are generated lazily and stop after two valid answers. Small parent
assignments are exhaustive; larger graphs use exact shared-root matching. Since seven or
more branch curves on at most two outer boundaries force at least four roots on one
boundary, a valid allocation proves multiple valid partitions. No search cutoff is
reported as user ambiguity. `SurfaceCreation` only
presents ambiguous drafts, with virtualized lists and shared validation before publication.

### Read-only tissue inspection

`application.tissue_inspection_stages` owns accepted-stage availability, provenance and
compatibility. `tissue_inspection` schedules owned, cancellable read-only comparison/point
jobs through the existing coordinator and validates their complete accepted read signatures
before publication. Authored pending status alone does not invalidate accepted geometry.
`native/inspection_*` owns material sampling, displacement buffers, region feather evaluation
and bounded spatial queries. Numerical results do not enter the authored document or undo.

The generic Issues provider contract now declares whether a detector is automatic. The
tissue geometry provider is manual: document changes invalidate existing evidence, never
schedule a scan. Explicit requests capture owned geometry, poses and neighbors at dispatch.
Results remain advisory. Existing inflation, smoothing, relaxation and stacking acceptance
are unchanged. The findings implementation shares the stacking translation unit because
qualified donor headers contain non-inline definitions; its exported query contract stays
separate from stacking evaluation and no competing worker pool is introduced.

The desktop owns stage presentation and native leases. `RenderModel`'s immutable staged
content carries buffer type, displayed stage, frame and mesh picking handle together, so a
mesh handle can never temporarily be interpreted as a colored-buffer pointer. Complete
replacements activate at the same frame boundary used by ordinary anatomy. Bounded x-ray
guides are a presentation overlay, not an edit to anatomy visibility. Native comparisons
retain their source/target meshes; profiler inventory attributes both buffers and leases.

Frozen inspection export validates stage/finding selection in the application layer and
normalizes the view to its JSON transport contract. The isolated renderer reconstructs the
comparison from the captured revision and includes matching point/finding evidence. The
desktop collector and report renderer do not become dependencies of headless geometry APIs.

### Visual inspection and material painting

Inspection query strategies own validation, read signatures, workload estimates and native
execution. The existing read-only job service owns snapshots, cancellation and publication;
route diagnostics use this service alongside tissue comparisons. Native route capture is
optional and bounded inside the production planner/solver. `curve_evaluation.resolve`
shares Fiber attachment/junction resolution between evaluation and inspection, preventing
a diagnostic path from silently ignoring bindings. Solver preferences are frozen at dispatch.

Painting caches native projection/visibility with owned mesh leases in the shared bounded
resource cache. Native material coefficients transfer brush coverage to field domains.
Desktop stroke state owns pointer samples and retains its last complete colored preview
while replacements are prepared. Only the shared paint commit operation edits the document.
The view cancels an obsolete stroke instead of committing it against changed anatomy.

Section contours are native queries; cutaways are view-local shader presentation. Native
clipped BVH traversal skips discarded candidates while preserving original geometry and
material identity. Section scope and plane masks are cached for repeated pointer queries.
Neither sections nor diagnostic paths participate in anatomical attachments/dependencies.
Goal inspection shares the production region-goal formula; reports distinguish accepted
source goals from retained bindings resolved against current target geometry.

Inspection signatures distinguish the immutable scene from presentation metadata. Camera
saves do not invalidate route evidence, section contours or a pending paint stroke; scene
edits still invalidate the conservative read set. Large overlay arrays cross the Qt boundary
through `ViewSnapshot` on change. Small status properties exclude geometry; this avoids QML
reference-sequence getters copying thousands of points repeatedly during bindings/rendering.

## Target-driven deformation and parameter-driven segment construction

`core/segment_chain.py` owns anatomy-neutral parameters; `native/segment_chain.cpp`
constructs capped profiles and uses the existing exact exterior union. Per-triangle
source identities and corner barycentrics preserve material locations when union
triangulation changes. Attachment captures own their reference resource through normal
history/checkpoint/job leases. A newly covered material location follows the same
union's nearest exterior in its retained construction chart, then the selected triangle
carries that location through downstream deformation. The original reference and
offset remain unchanged, so an exposed-again patch resolves to its original material.
The native chart retains untrimmed source triangle positions; shell layers are isolated,
and the chart participates in persistence, equivalence and resource accounting.
Legacy accepted surfaces remain readable; a new construction evaluation supplies the
chart without blanket startup recomputation. Unstable generated vertex memberships
are rejected by shared construction validation; cage controls remain independent.

Shrinkwrap bindings reference surface roles rather than dummy controls. Reference
queries, deletion/copy policies and the dependency graph consume those relationships;
workers use dispatch-time owned target geometry and target-local frames. Numeric work
runs in the existing native library; no Blender runtime or new worker pool is introduced.
Linear subdivision and vector displacement use the same ordered stage contract.

Attachment admission partitions multi-pose batches at intervening non-pose outputs.
Direct pose chains remain batched; pose/control/geometry/child-pose chains can publish
between batches without creating a job-level cycle. The coordinator still enforces all
read sets, output reservations, safe cancellation, undo and save checkpoint semantics.
The desktop value adapter converts identity-free typed parameter records to owned QML
values; identity-bearing records retain existing incremental projections.

## Opening and publication cost

Document snapshots own current record maps and reuse validated relationships. Per-record
links are cached only with a matching parent/type/junction context. Known evaluated-only
fields may reuse registry validation; new authored fields conservatively invalidate it.
Stack provider plans remain graph inputs. Pending tissue results publish in one batch.

Accepted SCP attachment receipts prove exact input identity across save/reopen without
changing the native attachment algorithm or introducing a distance tolerance. Absent or
changed receipts evaluate normally. They contain values/resource identities, never handles.

Fixed-output calculations may opt into renewable pending contracts: uncaptured requests
coalesce under one coordinator identity/deadline, with dependency-index renewal before
dispatch. Captured jobs retain safe cancellation and publication read validation. Explicit
cancel, undo, attachment recapture and payload-owning operations keep their existing rules.
Final tissue jobs also retain restart contracts: a changed stack plan can switch from
one output to a coupled group, which requires selecting a new evaluator and reservations.
Desktop command-line project opening uses the same background read/adoption path as File
Open; the window no longer waits for startup computations before it can be created.
## Shortcut observation and presentation (0.3.1)

Session-owned shortcut observation records causal IDs independently of attachment-edit
contexts. Coordinator submission, coalescing, retry and terminal notifications supply
evidence; the observer does not change reservations, priority, execution or publication.
The authoritative dependency graph supplies potential influence, while observed publications
and current output readiness supply completion. Related active work avoids repeated full
readiness scans. Formula values retain compact evaluation evidence outside document state.

Desktop adapters consume shared inspection operations and incremental models. Optional
effect masks own their Qt geometry in a lazily loaded scene, reading the same native
handles as the staged renderer; they release that scene when disabled. Native anchor
queries use owned revision-qualified inputs through the existing read-only job service.
No second scheduler, property engine, attachment solver or persistence format is added.
