# Local authoring API, 0.3.2

The 0.3.3 performance work adds no public commands. The
[addon functionality audit](addon_functionality_audit.md) distinguishes supported
operations from missing convenience/lifecycle operations; known migrated-assembly
limitations are in [parity findings](addon_parity_findings.md).

## Mirroring operations (0.3.5)

See the [confirmed specification](specification_035.md) and
[implementation plan](implementation_035.md). Shared operations cover source
mirror rules/inheritance, plane conflict overrides, instance/source inspection,
same-target attachment choices, removal blockers, mirrored rows, symmetric loops and
presentation. The [runtime command table and example](mirroring_035.md#shared-operations)
give concrete signatures, typed references and schema-6 storage behavior.
Mirrored properties, geometry, controls and shortcuts are read-only through every API
path. Typed surface references must distinguish the spatial instance and role; mirrored
geometry always reflects source output, without independent attachment/routing/stacking
solves. Existing independent counterparts require a separate explicit migration.

`measurement.point(entity, triangle, weights, role="", stage="")` accepts source or
instance identities and either an anatomical role or an explicit accepted tissue stage.
Witnesses remain frozen; plane/geometry changes mark them stale rather than rebinding.

## Shortcut comparison and replay (0.3.2)

`shortcut.comparison.capture(shortcut)` replaces the session-only accepted baseline.
`shortcut.comparison.inspect(refresh=False, wait=False)` reports readiness, replay
completeness and optional native geometry differences. `shortcut.comparison.clear()`
releases it without an authored edit. Capture during work is supported and labeled.

`inspection.export` adds `comparison=True` and `replay=False`. Replay explicitly includes
the complete starting project. `inspection.replay(path, output="")` validates the report
and executes supported operations in an isolated session with in-memory preferences;
it never edits the caller's document. See [archive contents, examples and limitations](shortcuts_032.md).

## Shortcuts and Parametric curves (0.3.0)

October 23 migration extensions are qualified in the
[migration record](tasks/skeleton-shortcuts-migration.md):
`curve.engine` accepts optional typed `settings` together with the engine switch in one
transaction. Parametric settings add `interpolation: "POLYLINE" | "BEZIER"` and
`bezier_resolution` (samples per segment, 1–1024). `resolution` still counts generated
knots. Retained Bézier modes/handle offsets preserve imported authored construction.
`curve.parametric.configure` edits these settings through the same topology policies.

Shortcut/driver `policy.scope` optionally identifies a controlled SCP for attachment
policies. Empty selects inferred ownership; explicit scope does not change All/Selected
grouping. `driver.configure(..., changes={"policy": {...}})` and `shortcut.configure`
share validation, copying, persistence and gesture contexts. Read-only
`world_transform.volume_scale` is the signed cube root of the affine determinant,
matching Blender's SCALE_AVG driver input even with shear/reflection.

The [walkthrough and operation signatures](shortcuts_030.md) describe
implemented property discovery, shortcut exposure/configuration/editing, driving-formula
lifecycle and policies, and Parametric definitions/variables. Desktop and headless clients
share these operations and their validation.

Ordinary property operations remain below wrappers; wrapper edits alone activate their
attachment policies. Both respect shared driven-property/type/topology restrictions.
There is no manual shortcut-owner or backsolve-target parameter. Existing curve-engine,
Fiber, junction, evaluation and transaction operations share the same command catalogue.
0.3.0 writes schema 5 and reads existing 0.2.4/schema-4 projects.

## Current operations

Existing operations and the 0.2.4 profiling additions remain available. Reports
include `tissue_preparations`, `collision_pairs` and `stacking_sessions` resource
categories and cache events. Stacking storage is a conservative upper bound because
the pinned solver owns an opaque cache. Preparation uses accepted geometry; no
authoring command changes are needed. See [performance qualification](performance_024.md).

The [0.2.2 tissue contract](specification_022.md) uses the same catalogue as existing
construction operations. Ownership and acceptance are in the
[implementation plan](implementation_022.md) and [release validation](development_status.md#unified-tissues-022).

## Tissue operations

`tissue.create(source, name?, preset?)`
accepts Point/Curve/Surface construction, including attached subclasses. Attached inputs
are reused and return the Tissue ID. Generic inputs create an independent attached graph
and return `{object_id, job_id}`; `wait` completes capture and downstream tissue evaluation.
The whole creation is one undo action; failure/cancellation publishes no partial graph.
`tissue.configure(target, changes)` edits general settings,
and `tissue.inflation(target, changes, part="main", side="a")` retains mode-specific data.
`tissue.relaxation(target, changes)` edits None/Geometric/Static PBD settings. Unsupported
combinations fail through the same capability policy in desktop and headless clients.

`tissue.preview(target, changes, part="main", side="a", reset="")` queues an owned
inflated-rest candidate without changing the document, undo history, save checkpoint or
accepted surface. Optional reset is PROFILE or CONTROL. `tissue.preview.status` returns
its token/state/settings; `tissue.preview.accept(token)` commits parameters in one undo
action using the shared inflation policy. `tissue.preview.cancel` discards it. Only a current
successful candidate can be accepted. Desktop **Preview inflation edits** renders a green,
unpickable candidate while keeping accepted geometry/picking; it shows rest inflation before
relaxation/crop/stacking. Selecting a different object cancels the desktop preview.

`tissue.constraint.add(target, mask="ALL", mode="FIXED", strength?, feather?, offset?)`
returns a region ID. Use `tissue.constraint.update(target, constraint, changes)` or
`tissue.constraint.remove(target, constraint)` to edit/remove it. Regions are source-relative
by default. `tissue.constraint.bind(target, constraint, parent, role?)` captures or explicitly
recaptures target-relative goals against accepted inflated rest geometry; it returns a job
ID. `tissue.constraint.unlink(target, constraint)` restores source-relative goals. Capture
and target movement preserve shared sources. Normal offsets follow the captured target
frame; changed rest topology requires explicit rebind/unlink. Contradictory exact goals
fail evaluation and retain accepted geometry. Iteration-limit solves can publish usable
output with a separate convergence warning.

`tissue.field.set(target, name, values, domain="BASE")` stores explicit normalized weights
against the accepted Base or Rest domain, including all-zero values. `INFLATION` is reserved
for normal-shell Base thickness weights; other names become custom constraint masks.
Incompatible topology changes require explicit replacement/removal of the field.
`tissue.field.remove(target, name)` requires removing its constraint references first.
`tissue.field.create(target, name, domain="BASE", value=0)` initializes a named field.
`tissue.field.assign(target, name, indices, value, topology)` assigns selected weights
through the native adapter and rejects stale material signatures. The desktop Weight fields
disclosure creates/selects/removes fields and assigns weights to selected material points.
Point colors distinguish zero, partial and full weight; generated vertex coordinates stay read-only.
Generated tissue transforms remain unavailable. Generic object deletion preserves sources.

Fiber creation binding rows accept an explicit `role`: `SCP_GEOMETRY`, `TISSUE_BASE`,
or `TISSUE_FINAL`. `fiber.binding.set(curve, point, target, scope?, role?)` uses the same
provider policy. Omitted roles choose the provider's ordinary surface (SCP geometry or
tissue final); an explicitly unavailable role is rejected. Captured material geometry
is retained through deformation and untouched endpoints are not recaptured during edits.
Desktop selectors show the role and availability. Automatic routing includes tissue final
surfaces; existing obstacle/exclusion IDs accept tissues. A base-bound Fiber retains that
explicit binding role. Failed roles are not replaced by displayed intrinsic fallback.
Accepted empty crops contain no collider; restoring geometry invalidates routes again.

Adaptive exact surfaces retain material coordinates independently of their evaluated
vertex counts. Anchor frames, dense Fiber influences and tissue target-region goals
resolve on the current Base/Final surface without changing captured bindings. Offsets
and orientation are transported in the same native query. This is automatic evaluation,
not a new authoring command. Authored topology restrictions and cropped-away material
errors remain enforced. Indexed weight fields/face selections still use their explicit
topology qualification.

`curve.point.update` also accepts Boolean `stacking_fixed`
and `protected_crease` fields. Bound Fiber points are protected automatically. Surface
evaluation retains these locations in its accepted material data; tissue refinement
preserves their exact coordinates. Manual surfaces keep their previous pin snapshot
until evaluated. Protection-only edits do not recapture Fiber attachments or alter shape.
The curve inspector exposes both flags.

`tissue.stacking.configure(target, changes)` controls search distance,
clearance, smoothing radius/strength, blend distance, preservation and maximum adjustment.
`displacement` is the native discovery allowance in metres (default 0.5, range 0..1000),
not a displacement clamp. `tissue.configure(target, changes={"group": "name"})` assigns
an automatic stacking group; matching nonempty names suppress automatic comparisons.
Names are trimmed, case-sensitive and at most 256 characters; empty means independent.
Explicit pair overrides are still eligible. Policy changes invalidate affected plans/read
sets while retaining accepted intrinsic geometry. `tissue.stacking.inspect` includes group.
`tissue.stacking.relationship(target, other, side="a", other_side="a", mode="AUTO",
cover="SELF", excluded=False, regions?)` saves persistent pair intent. Modes are AUTO,
REQUESTED (must agree with geometry) and EXPLICIT (still independently validated); cover is
SELF or OTHER. Regions are `[part_identity, material_face]` pairs on the covering tissue,
captured against its accepted Base topology. Omitted existing region settings are retained.
`tissue.stacking.remove(target, other, side="a", other_side="a")` restores automatic behavior.
`tissue.stacking.inspect(target)` returns settings, intent, detected order/providers and final
status. Both surface participants opt into stacking; disabled inflation sides remain inactive.
The desktop Stacking disclosure provides searchable tissue pairs, settings and order/exclusion
editing with ordinary undo. Requested/Explicit relationships provide **Select support footprint**:
click covering faces to toggle a non-mutating draft, inspect its green outlines, then Accept or
Cancel. Empty selection explicitly uses the entire footprint. Optional `topology` on a region
assignment rejects a stale caller; unknown parts/faces and implicit cover changes are rejected.
No successful final surface is published from failed stacking.

## Construction commands

The desktop and headless clients share these operations, policies and transactions.
See the [construction walkthrough](construction_020.md) and
[release validation](development_status.md#construction-objects-020).

Attached-point operations added in 0.2.2:

| Operation | Arguments | Result |
| --- | --- | --- |
| `construction.point.create` | optional `name`, `position`, `parent`, `owner`, TRS `values` | Point ID; omitted position uses the workspace cursor. |
| `construction.point.update` | `target`, local `position` | Ordinary Point edit; Anchors require explicit rebind. |
| `anchor.create` | Point `source`, optional anatomical `parent`, `role`, `name` | Independent Anchor creation with object/job IDs; source unchanged. Omitted parent chooses nearest ready SCP. |
| `anchor.rebind` | Anchor `target`, anatomical `parent`, optional `role`, world `position` | Capture job ID; omitted position retains the current resolved location. |
| `surface.create` | exclusively Fiber `curves`, existing surface settings | Creates a Membrane through the shared surface evaluator; mixed sources remain generic. |
| `membrane.create` | Surface `source`, optional `name` | Object/job IDs for one independent attached graph; ordinary sources become Fibers, existing Fiber bindings and internal junction sharing are preserved. |

`parent` in Anchor capture names the anatomical target, not ordinary transform parenting.
Explicit roles are `SCP_GEOMETRY`, `TISSUE_BASE` and `TISSUE_FINAL`; unavailable roles fail.
Automatic conversion chooses SCP geometry only; use explicit Anchor/Fiber targets when
Tissue Base/Final bindings are intended. Surface correspondence, exact sampling, branch
identities and source transforms are remapped without changing the original construction.
Generic inspection, naming, deletion and Make Independent retain their existing meanings.
Primitive `curve.point.*` operations are unrelated to construction-point lifecycle.
See the [tissue walkthrough](tissues_022.md) and [executable example](../examples/tissues.json).

| Operation | Arguments | Result |
| --- | --- | --- |
| `curve.create` | optional `name`, `points` (CurvePoint records), `parent`, anatomical `owner`, `engine`, typed `settings`, `closed`, TRS `values` | Independent curve ID; BEZIER default; POLYLINE and ROUTED supported; no SCP needed. |
| `curve.edit` | `curve`, optional `name`, `closed`, `resolution` | Shared authored edit; validates all consumers' topology locks. |
| `curve.point.update` | `curve`, `point`, point/handle/radius/tilt fields | Shared point edit using native handle behavior. |
| `object.inspect` | `target` | Typed authored construction record and consumer IDs. |
| `object.rename` | `target`, `name` | Metadata edit without geometry scheduling. |
| `object.transform` | `target`, nine TRS `values` | Ordinary local transform; rejects whole-fiber transforms. |
| `object.reparent` | `target`, optional `parent` | Preserves world placement and consumer placement. |
| `object.delete` | `target` | Blocks referenced sources; preserves ordinary children. |
| `object.delete.inspect` | `target` | Read-only shared validation and impact query; returns command/arguments and affected object IDs/names. Desktop asks for confirmation only when other objects are affected. Actual deletion revalidates current state. |
| `primitive.from_curves` | ordered `curves`, `kind` BODY/LOFT, optional `parent`, `name`, `shape` | SCP ID with live curve references. |
| `primitive.curve_mode` | `entity`, `curve`, `mode` SHAPE_ONLY/SHAPE_AND_TRANSFORM | Changes transform following without a visible jump. |
| `primitive.make_independent` | `entity`, `curve` | New curve ID; remaps that consumer and its memberships. |
| `consumer.sampling` | `entity`, `curve`, `samples` | Consumer-owned override; null inherits primitive density (32 for surfaces). Incoming attachments lock changes. |

Primitive inspect retains resolved curve records for editing clients; project storage
holds references and separate objects. Schema 4 rejects earlier schemas, including 3. Standalone path
evaluation and explicit engine conversion, including native routing, are described below.

## Existing command catalogue

The [0.2.0 contract](specification_020.md) adds object/curve/fiber/surface/image operations
and retires direct control-surface attachment. The commands below are implemented; release
qualification is tracked in [the implementation record](tasks/020-construction.md).

The desktop and JSON clients call application/commands.py. A request has operation,
arguments (an object) and optionally id. Success responses contain ok, revision and
result; failures contain ok=false, error and revision. An ID stores the result for
later references such as "$root.entity_id". No Python expressions are evaluated.

run accepts a JSON array; serve accepts one JSON object per stdin line and returns
one response per stdout line. Native import diagnostics may appear on stderr.
serve continues scheduling between requests. Ending the process does not save.

| Operation | Arguments | Result/meaning |
| --- | --- | --- |
| import | path, units; optional parent, y_up=false, name | entity_id and job_id; one SCP per file |
| scp.empty | name; optional parent | New empty SCP ID |
| scp.wrap_root | optional name="Assembly" | New empty root ID |
| scp.rename | entity, name | Change display name |
| scp.color | entity, value="#RRGGBB" | Authored SCP colour |
| scp.transform | entity, values=[x,y,z,rx,ry,rz,sx,sy,sz] | World transform; metres and Euler degrees |
| scp.duplicate | entity; optional parent | Independent subtree copy ID |
| scp.delete | entity | Remove only this SCP and preserve children; returns the new parent/group ID, or empty string |
| scp.reparent | entity, parent | Preserve pose, change relation and capture |
| scp.attachment | entity and any settings below | Change/capture attachment |
| scp.recapture | entity | Queue capture from the current pose |
| scp.origin | entity | Move origin to captured anchor while preserving mesh position |
| attachments.enable | enabled | Freeze/rebind all attachments |
| update_mode | mode; optional entity | LIVE, ON_RELEASE, MANUAL; per-SCP also INHERIT |
| begin / commit / cancel | none | One editing transaction |
| undo / redo | none | Navigate authored history |
| evaluate | optional entities=[SCP IDs] | Evaluate selected construction, required prerequisites and attachments; omission selects all |
| tick | none | One scheduler dispatch/publication pass |
| wait | optional timeout in seconds | Drain running and queued jobs |
| job.cancel | job_id | Request cooperative cancellation |
| job.retry | job_id | Restart a retryable terminal job |
| inspect | none | Current entities, jobs, checkpoint and workspace |
| inspect.target | entity (SCP or control ID) | Read-only relationships, attachment/frame, revision, geometry and topology-lock details |
| inspect.snapshot | optional entities=[IDs] | JSON inspection with full issue coverage/freshness; no Qt initialization |
| inspection.export | path ending .afinspection.zip; optional selected="", editing=false, wait=false | Frozen current revision, image/JSON archive; returns job/path/revision/state; read-only background work |
| units.convert | value; optional source="m", target="m" | Convert length between m/cm/mm; API geometry always uses metres |
| workspace.remove | index > 0 | Remove named workspace; active removal selects whole document |
| workspace.preset | name=all/shape/surface/attachments | Apply category show/select preset |
| save | path, blocked_policy | Saved revision/path or pending jobs |
| open | path | Load the project and queue equivalent SCP startup synchronization |
| workspace.create | name, members; optional children=false | Create and activate focused workspace |
| workspace.select | index | Activate named workspace |
| workspace.update | presentation settings below | Update active workspace without an anatomical undo step |
| profile.start | optional seconds=120, memory_mib=128 | Start explicit runtime recording without an authored edit |
| profile.status | none | Recording/export state, storage, output path and collector health |
| profile.stop | optional path, wait=false | Freeze and export, or retry failed export; headless can wait for completion |

`workspace.create` accepts mixed SCP/control `members`; `children=true` expands only
SCP descendants. `workspace.update` accepts an optional `index` (default active),
`name`, `members`, `display_units` (m/cm/mm), `hidden_categories` and
`unpickable_categories` in addition to existing camera/object/overlay settings.
Categories are geometry/curves/points/handles/hooks/cages/anchors; anchors are visual
markers. The whole-document workspace cannot restrict membership. New unknown
references are rejected; references retained for undo after deletion are allowed.
See [workflow inspection](workflow_inspection.md) for archive contents and CLI usage.
Profiling operations use a session-owned runtime service, outside the document command
catalogue and save checkpoints. See [profiler report/API details](profiling.md).

Parent is required when adding to a populated document; an empty document's first SCP
is the root. The root cannot be reparented; wrap it in an empty root first. Imported
geometry is immutable, while its transform and attachment remain editable.
units is metres per source unit: 1 for metres, 0.01 for centimetres, 0.001 for millimetres.

Deleting an SCP promotes its direct children to its parent, preserving world poses and
recapturing attachment bindings. A root with children is replaced with an empty grouping
root at the former root's pose; a leaf root leaves an empty document. Referencing controls
detach at their accepted world pose, other consumers remain, and obsolete jobs cannot publish.
Deletion is one undoable operation and indirect child changes respect the full dependency
graph even outside the focused workspace. This intentionally replaces 0.1.2 subtree deletion.

Attachment settings:

- parent_mode: SURFACE_NEAREST or OBJECT_ORIGIN.
- child_mode: FACE_CENTER, VERTEX_NEAREST or OBJECT_ORIGIN.
- strategy: AUTO, STABLE_SURFACE or DEFORMATION_FLOW.
- follow_rotation: boolean.
- face_lock and vertex_lock: canonical zero-based indices, or -1 to clear.

Workspace settings include name, members (SCP/control IDs), focused, hidden, unpickable,
camera=[x,y,z,pitch,yaw,roll,distance], orthographic, handles, anchors and diagnostics.
Presentation camera angles are degrees. Setting a workspace does not remove entities or
relations from the document. Its outside entities are read-only for authoring commands.

save requires an explicit policy even if no calculation is running:
wait drains document-writing calculations; checkpoint saves the historical committed revision when blocked;
pending reports that saving is blocked without writing. Read-only background work does
not block commitment. A failed calculation is terminal and its failed state can be saved.

Opening still queues SCP startup synchronization. Accepted attachment poses now carry
exact input receipts (including evaluator version); matching inputs retain the saved pose
without floating-point drift or downstream invalidation. Missing/changed receipts use the
normal native evaluation. Schema-4 projects without receipts remain readable. Receipts are
derived output, not authoring parameters; use the attachment operations for rebinding.
Queued fixed-output requests may share a job ID until input capture. Explicit cancellation,
undo, read validation and checkpoint rules remain unchanged.

Use begin/update/commit for a drag-like sequence. A single editing command implicitly
creates one transaction. Manual mode needs evaluate. Do not infer calculation completion
from a returned job ID: use wait or inspect jobs. File inspection and revision-matched GPU
capture also have process-level CLI commands documented in quickstart.md.

## Measurement and camera operations

These operations use the active workspace. Measurements freeze two picked world-space
surface points; they do not calculate minimum clearance between whole meshes. Distances,
XYZ and delta coordinates are always metres in the API, regardless of display units.

| Operation | Arguments | Result/meaning |
| --- | --- | --- |
| measurement.point | entity, triangle, weights=[a,b,c] | Validated surface witness from accepted geometry: IDs/revision, barycentric coordinates, world position and frame |
| measurement.add | start, end (witness records); optional name="Distance" | Persist frozen ruler; returns ID |
| measurement.list | none | Endpoints, delta XYZ, Euclidean distance and stale status |
| measurement.remove | measurement (ID) | Remove ruler from active workspace |
| bookmark.add | name | Save current workspace camera/projection; returns ID |
| bookmark.list | none | Named cameras and IDs |
| bookmark.restore | bookmark (ID) | Restore exact camera/projection; return bookmark record |
| bookmark.rename | bookmark, name | Rename saved view |
| bookmark.remove | bookmark | Remove saved view |

Rulers become stale when their source surface or frame changes or disappears. They retain
their captured values and do not keep mesh allocations alive. Desktop picks capture the
displayed revision even while newer geometry is staging. Bookmarks preserve active edit
transactions; desktop restoration rebases the current gesture without moving geometry.
All annotations are workspace presentation, persisted outside anatomical undo. Annotation
changes are rejected while the save-wait edit lock is active. Inspection archives include
the frozen rulers, stale flags and workspace bookmarks. See the [walkthrough](workflow_inspection.md).

## Issue reporting operations


All operations use the session issue system; numerical headless use initializes no Qt.
See [component responsibilities and coverage](issues.md) and the executable
[JSON example](../examples/issues.json). Rechecking never repairs or changes undo state.

| Operation | Arguments | Result/meaning |
| --- | --- | --- |
| issues.list | optional filters={}, text="", offset=0, limit=100, include_dismissed=false | Paginated records and whole-document check coverage; maximum page size 200 |
| issues.status | none | Repository revision, issue/dismissal counts, check states, complete and clean flags |
| issues.get | identity | Finding, immutable evidence, source identity, target/related IDs, freshness |
| issues.recheck | optional provider | Request a fresh check from one/all available providers |
| issues.cancel | optional provider | Cancel queued/running diagnostic checks; retained evidence becomes stale |
| issues.dismiss | identity, optional dismissed=true | Hide current finding; false restores it |
| issues.fixes | identity | Applicable explicit repair names/labels; empty when stale or read-only |
| issues.fix | identity, name | Start registered repair; result is not proof of resolution |
| issues.repairs | none | REQUESTED/VERIFYING/DONE/FAILED/CANCELLED/UNRESOLVED records |
| issues.cancel_fix | identity | Request safe cancellation of a repair's submitted jobs |

Filters are provider, scope, target, kind, stage, severity and code. Invalid filters
are rejected. Status/coverage is global even when the returned rows are filtered.
Use `wait` to finish queued checks and repairs, then query again. A check can finish
successfully while reporting a defect. Failed checks retain earlier evidence with
`freshness=stale`; an empty filtered page is not a clean certificate. Dismissals and
check records are session state and reset on opening a document or navigating history.
Built-in providers are evaluation.v1, dependencies.v1, fiber_collisions.v1 and the direct
lifecycle producer tasks.v1. Only asynchronous detectors can be cancelled. Registration ports
for Python integrations are `session.issues.listening.register(Provider(...))`,
`session.issues.reporting.report(Issue(...))`, and `session.issues.resolution.register(Solver(...))`.

## Primitive and shared-control operations

IDs returned as strings can be used as `$loft` or `$hook`; nested result references
also accept array indices, e.g. `$definition.primitive.curves.0.id` after an inspect.
See [examples/primitives.json](../examples/primitives.json) for a complete batch
creating a connected loft, Hook-driven cage, thickness, curved capsule and import.

| Operation | Arguments | Result/meaning |
| --- | --- | --- |
| primitive.create | kind=LOFT/BODY; optional parent, name, shape=BOX/CYLINDER/CAPSULE, definition | New SCP ID; initial geometry is pending until evaluated |
| primitive.update | entity; samples, strips, start, span, caps | Construction settings; strips/range/caps are loft-only |
| primitive.inspect | entity | Definition, ordered bindings, accepted result/provenance and topology dependents |
| curve.add | entity; optional source curve ID | Add a curve, or independent copy; BODY also gains a piece |
| curve.remove | entity, curve | Remove owned curve/piece; first remove bindings targeting it |
| curve.order | entity, curves=[all owned IDs] | Set complete curve order |
| curve.split | entity, curve, segment, parameter | Split a zero-based Bézier segment at 0 < parameter < 1; returns the new point ID |
| curve.update | entity, curve; name, closed, matrix, start, span, resolution | Curve coordinates, evaluation and optional loft sampling override |
| point.insert | entity, curve, index, point={...} | Insert a Bézier control point |
| point.update | entity, curve, point; position, left, right, left_mode, right_mode, radius, tilt | Geometric edit; handles follow Blender modes |
| point.remove | entity, curve, point | Keep at least two points |
| body.update | entity, piece; shape, width, depth, fit, length, position, sides | Body piece settings |
| thickness.update | entity; optional remove=true, or Simple Solidify settings below | Separate editable thickness after geometry deformers |
| control.create | optional kind=HOOK/LATTICE, entity, name, values | New shared control ID; follows entity or document; lattice fits entity unless values supplied |
| control.transform | control, values=[x,y,z,rx,ry,rz,sx,sy,sz] | Ordinary parent-local TRS, or world TRS without a parent |
| control.follow | control; optional entity="" | Follow any eligible ordinary transform source, preserving world placement; images cannot be parents |
| control.update | control; name, interpolation, outside, weights | Shared settings |
| control.affected | control | Affected SCP IDs, including indirect consumers |
| control.delete | control | Remove this control and its bindings; return deleted/affected IDs |
| lattice.point | control, index, position=[x,y,z] | Cage-local authored coordinates |
| lattice.resize | control, resolution=[u,v,w] | Native linear transfer, restored interpolation and cleared cage weights |
| deformer.add | control, target; optional indices, settings below | New binding ID; Hook binding initially preserves selected coordinates |
| deformer.update | binding; enabled, strength, indices, weights, invert and Hook settings | Update per-target influence; identity/target/control changes use explicit operations |
| deformer.members | binding | Current resolved member indices |
| deformer.order | target, bindings=[all IDs for that target] | Reorder only this target stage |
| deformer.remove | binding | Remove influence, preserve other consumers and authored primitive |
| hook.reset | binding | Reset binding transform using current target/control frames |
| hook.recenter | binding, center=[x,y,z] | Set target-local falloff center |

In 0.2.0 `control.attach` is retired and rejected as an unknown operation. Hook and
lattice controls never have anatomical bindings. They appear in Construction;
workspace inclusion follows their anatomical associations and deformer consumers,
while explicit workspace membership accepts anatomy only. Ordinary following does
not lock topology. Deleting a transform parent preserves its children's world frames.

`target` is `{owner, stage, component}`. Default stage GEOMETRY uses an SCP's generated
vertices. CURVE requires its owned curve ID; BASE requires a BODY piece ID; LATTICE
uses a cage control as owner and supports Hooks. GEOMETRY/LATTICE omit component.
Curve membership uses Blender's left-handle/point/right-handle triple indices.
Commands convert them to stable authored point identities; insertion preserves existing
membership and weights. Mesh/base/cage indices refer to the target's native point order.
Omitted indices bind all points; an explicitly empty list binds none.

Curve definitions contain points, name, closed, matrix, resolution and optional
start/span. Points contain position/left/right triples, AUTO/ALIGNED/FREE/VECTOR handle
modes, nonnegative radius and tilt in radians. IDs can be supplied explicitly but must
be unique across the document; omitted IDs are generated. Body definitions list pieces
referencing owned curve IDs. A BODY needs at least three longitudinal samples.
All coordinate matrices are row-major affine 4x4 arrays in metres; transform commands
use Euler degrees. Loft sampling ranges are normalized, and body position/length use metres.

Hook settings: strength, radius, falloff (NONE, CURVE, SMOOTH, SPHERE, ROOT, SHARP,
LINEAR, CONSTANT, INVERSE_SQUARE), uniform, center, weights, invert, custom (flat XY
pairs), custom_handles (AUTO/VECTOR/AUTO_CLAMPED per pair), custom_extrapolate.
Custom X coordinates must increase. Influence weights must match the target point count.
Lattice controls use per-axis LINEAR/CARDINAL/CATMULL_ROM/BSPLINE interpolation, Outside,
and optional cage weights; bindings separately own strength and target influence weights.
Resolution is clamped by Blender-compatible limits: 1–64 per axis, at most 32,000 points.

Simple Solidify settings: enabled, thickness, offset [-1,1], rim, rim_only, even,
high_quality_normals, flip, clamp [0,2], angle_clamp, weights, invert and minimum [0,1].
Weights refer to the unthickened mesh. Enabling/disabling/removing thickness or changing
its topology settings obeys attachment locks. Complex mode and Apply/Bake are unavailable.

`inspect` reports shared controls and accepted results. Result `inputs` records owner,
output port, authored revision and accepted revision; `pending` names upstream Manual
inputs with newer authored changes. Failed cycles retain previous geometry and finish
unsuccessfully, so they do not block saves indefinitely. Read `jobs` and result status
after `wait`; successful command dispatch alone does not guarantee successful calculation.

The released 0.1.x implementation used schema 2 with version-1 migration; 0.2.0/0.2.1
used schema 3. Current 0.2.2 uses **schema 4 only** and clearly rejects all earlier
formats. Native handles and undo history are never serialized.
## Reference images

Image operations use the same session command API, with no Qt dependency:

- `image.import(path, width=1, name="", parent="", owner="", values=None, axis="")` returns
  `object_id` and `job_id`. PNG/JPEG decoding and native preparation are asynchronous.
  `values` uses the existing position/rotation/scale convention, in metres/degrees.
  Optional `axis` X/Y/Z sets world-axis orientation while preserving the initial world
  position and scale, including beneath a rotated ordinary parent. Omit it to retain
  the supplied local orientation. Parenting and initial alignment share the import undo step.
- `image.replace(target, path)` replaces one assignment asynchronously. Position and
  physical width remain; height follows the new aspect ratio; landmark calibration clears.
- `image.instance(source, name="")` creates an independent placement sharing its image asset.
- `image.size(target, width)` preserves aspect ratio and clears landmark calibration.
- `image.align(target, axis)` faces world X, Y or Z while retaining position and scale.
- `image.calibrate(target, first, second, distance)` takes two normalized image UV points
  (top-left origin, each component in `[0,1]`) and a positive world distance in metres.
  Native calibration respects the complete parent/world transform and creates one undo step.
- `image.inspect(target)` returns asset identity, pixel dimensions, format, physical size
  and calibration status. Generic `object.inspect`, `object.transform`, `object.reparent`,
  `object.rename` and `object.delete` also apply. Images cannot be transform parents.
- `image.presentation(target, **settings)` updates the current workspace without anatomical
  undo or geometry work. Settings: `opacity` (0–1), `depth` (`NORMAL`, `FRONT`, `BACK`),
  `side` (`BOTH`, `FRONT`, `BACK`), `orthographic`, `perspective`, `only_axis_aligned`,
  and `pickable`. Axis-only visibility uses Blender's local-Z/view-axis tolerance and
  affects both drawing and picking without changing the image's transform.

`wait` includes image jobs. Import/replacement uses the initiating undo step; cancel/failure
never publishes a partial image. Source bytes are embedded once per unique asset in schema 4.

## First-class drawing

`curve.create` creates an editable standalone curve; no SCP is required. Its optional
placement defaults to the workspace 3D cursor. `curve.draw(points, settings)` accepts
world-space xyz or xyz/radius samples, fits asynchronously and returns `object_id` and
`job_id`. A complete accepted curve is published into the initiating undo entry.
Settings: `method` (`REFIT`, `SPLIT`, `POLYLINE`), `error` in document units,
`corner_angle` in radians, and `closed`. Fitting remains editable, with no baked-only path.

`drawing.project(rays, plane, surfaces, image, settings, interpolate)` is a Qt-free
read-only operation. Each ray is `[ox,oy,oz,dx,dy,dz,screen_x,screen_y,radius]`.
`plane` is `[px,py,pz,nx,ny,nz]`; `surfaces` lists SCPs with accepted geometry.
Projection settings: `depth` (`VIEW`, `SURFACE`, `IMAGE`), `first_plane` (0 follow,
1 view, 2 surface, 3 tangent view), `offset`, `relative`. IMAGE depth uses `image`'s
world plane. Returned xyz/radius samples can be supplied to `curve.draw`; neither
operation creates an enduring source-image/surface relationship. Surface snapshots use
accepted results; desktop drawing instead captures the exact displayed revision.

Native projection uses exact triangle queries rather than Blender's depth-buffer pixels.
The first-hit/fallback/offset policies are adapted from Blender 5.0.1. Fitting uses its
pinned curve_fit_nd implementation. Cancellation is checked around the atomic fit call;
obsolete output cannot publish. `tools/drawing_qualification.py` records this interval.

## Curve engines and optional conversion

Authored curves store typed `engine_settings`: Bézier (`kind`, `resolution`), exact
polyline (`kind`), or routing (`kind`, `samples`, `radius`, `accepted_steps`, `obstacle_mode`,
`obstacles`, `excluded_obstacles`).
There is no public solver generation selector. `curve.create` accepts `engine` and a
`settings` dictionary; the existing Bézier `curve.edit(resolution=...)` operation remains
an alias for its typed setting. Curve/Fiber consumers still share the same path contract.

`curve.engine(curve, engine)` directly selects BEZIER, POLYLINE or ROUTED as one undoable
edit. It retains all authored points, handles and identities; Fiber edits use their current
resolved authored points and preserve bindings. The chosen engine defines the new path,
without resampling accepted output. Selecting the current engine is a no-op. A different
engine starts with its typed defaults (routing samples are at least the authored point
count), respects shared topology/workspace policies and follows ordinary task/update modes.
The authored selection changes immediately; pending or failed evaluation retains accepted
geometry. This is the desktop Path engine selector's command.

The separate optional preview API supports explicit resampling or point-subset conversion:

- `curve.conversion.preview(curve, engine, mode="EVALUATED", samples=64, points=None, settings={})`
  starts a read-only coordinator job. EVALUATED resamples the accepted path into editable
  vector-handle points; AUTHORED retains authored points. Routing selects AUTHORED and retains
  all existing authored points when `points` is omitted. An explicit subset must retain open
  endpoints, anatomical bindings and junctions; an explicit empty list fails.
  Sampled conversion retains bound point identities and positions, allocating its exact
  point budget between required anchors in native work. Insufficient budgets fail explicitly.
- `curve.conversion.status()` returns the token, job, state and candidate point count/settings.
- `curve.conversion.accept(token)` validates the captured read set and shared topology locks,
  then commits one undoable edit. It preserves metadata edited after preview and retains
  accepted geometry while the converted path evaluates.
- `curve.conversion.cancel()` releases the candidate and cancels pending preview work.

Only one preview is retained. It does not alter saving, document state or undo; it is not
serialized. The desktop displays it in green and excludes it from picking. Source edits
invalidate acceptance. Routing runs through the native production solver and the existing
coordinator. `curve.engine_settings(curve, **settings)` changes
the current engine's parameters; use `curve.engine` for ordinary engine changes.
Routing defaults to `obstacle_mode="AUTO"`: every SCP geometry provider is eligible,
minus `excluded_obstacles` and automatic cycle exclusions. Fiber binding/support surfaces
remain required. Visibility and workspace do not remove obstacles. `MANUAL` uses explicit
`obstacles`; providing that field without `obstacle_mode` retains manual API intent, including
an empty list. Set AUTO explicitly to adopt automatic selection. Auto cycle exclusions
cannot hide explicit cycles. Project schemas earlier than 4 are rejected before decoding.
All eligible surface poses/results and structural scene membership are declared inputs.
New/deleted providers invalidate pending work/previews. Missing accepted inputs fail rather
than becoming empty space. Manual inputs retain accepted geometry and pending provenance;
publication triggers consumers at their workspace priority. Failed solves retain accepted paths.
The inspector keeps clearance accessible and moves sampling/iteration settings to Advanced.
Routing `samples` is a preferred total: the evaluated path may contain more points to
retain obstacle-avoiding bends and authored knots. The authored setting stays unchanged.
`object.inspect` reports the accepted geometry's actual `samples`; consumers retain
their own sampling settings and topology locks. Solver preparation preserves the same
validated layout for geometry, fixed knots and reference parameters. Growth is bounded
by the existing one-million-point native limit. Clearance and iteration caps do not
adjust automatically.

Accepted Bézier/polyline fibers are checked by the read-only `fiber_collisions.v1` Issues
provider. `issues.recheck` and `issues.cancel` use the ordinary advisory coordinator. A
`FIBER_COLLISION` finding identifies the fiber, intersected SCP, first offending sampled
segment, accepted path/surface assets and numerical tolerance. Segment crossings and closed
mesh containment are checked, including the closing edge. Only tiny neighborhoods around
explicit bound knots permit their expected surface contact. This is a centerline check of
the accepted sampled path, not a continuous Bézier proof or a physical fiber-radius test.
It never changes engines, geometry, undo history or save checkpoints. Stale captures cannot
publish current findings; failed or cancelled checks remain explicitly incomplete.
Pinned actual-addon fixtures cover cold/warm skull routes, attachment deformation and surfaces.
Recorded shared-fiber profiling includes preparation, publication and resource release; evidence
and its limits are in [release validation](development_status.md#construction-objects-020).

### Fiber creation

`fiber.create(curve, bindings=None, name="Fiber")` starts an asynchronous independent copy.
Omitting bindings uses both open endpoints, or the first closed-curve point, with native
nearest-ready-SCP capture. Explicit binding rows may omit `target` to use the same
automatic choice for that point; explicit Tissue Base/Final overrides remain supported.
Automatic candidates and coordinates are captured at dispatch, not when queued.
Dense deformation support is a separate policy from choosing an endpoint: skeletal
fibers capture eligible SCP surfaces, while explicitly tissue-backed fibers use only
their selected parents (including selected SCPs). Nearby unrelated tissues do not
become implicit deformation parents. Current-shape editing uses this same policy;
`ANY_PARENT` still permits explicitly edited endpoints to choose an eligible tissue.
Each binding is `{point: authored_point_id, target: anatomical_surface_id,
capture_scope: "CURRENT_PARENT" | "ANY_PARENT"}`. Supply both open endpoints or
at least one point on a closed curve. It returns the job identifier; completed creation
appears in the Construction registry as `kind: "fiber"`. The source has no continuing
reference to its copy. Invalid/incomplete bindings leave an ordinary curve unchanged.

Direct `object.transform` on a Fiber is rejected before mutation. Use generic curve-point
operations to shape fibers; their anatomical bindings and ordinary transform parenting
remain supported. Desktop creation waits for an accepted object, exits component editing
and selects the result unless the user has moved to a newer editing context. This selection
intent does not change the headless command's job-ID result or its undo behavior.

The accepted path follows captured anatomical surfaces through the common coordinator.
Dense attachment fields are independently owned project resources; source edits cannot
change them. Current-shape point edits use the ordinary curve operations. They retain the current dense
shape, rebind changed anchors and preserve unchanged canonical anchors in the same transaction.
`fiber.binding.scope(curve, point, scope)` chooses `CURRENT_PARENT` or `ANY_PARENT` for a
bound authored point. `fiber.binding.set(curve, point, target, scope?)` adds or reassigns a
binding at the current shape; using its existing target explicitly recaptures it.
`fiber.binding.remove(curve, point)` removes an optional structural binding. Both open
endpoints and at least one closed anchor must remain bound. Extend or remove an open
endpoint to transfer its parent choice to the new endpoint; opening a closed fiber requires
choosing both endpoint bindings first. Pending capture requests survive Manual-mode saving.
Parent movement resolves its retained binding without choosing a new
parent. Entering edit mode is a read-only query. Routed fibers edit authored constraints,
then resolve their connecting path through the solver. Independent copies remap attachment
resource owners, routing obstacles and pending edit baselines together. Shared immutable
geometry buffers remain retained by their resource owners. These are construction operations;
they do not certify anatomical accuracy or reconstruct muscles.

## Tissue creation and material cropping

`tissue.create(source, preset)` applies editable defaults for `MUSCLE`, `CUSTOM`,
`CLOSED_BULK` (Anchor), `RIM` (Fiber), and `LAYER`/`POUCH` (Membrane). Incompatible
source/preset combinations fail before creation. All presets use the same TissueVCP.
`tissue.configure(..., changes={"classification": "..."})` changes only its label;
it never reapplies defaults or changes stacking. See [release validation](development_status.md#unified-tissues-022)
for numerical/visual evidence and its limits.

Tissue acceptance checks finite coordinates, canonical connectivity and newly collapsed
faces. Self-intersections within one tissue are explicitly permitted; inflation and
smoothing formulas are unchanged. Failed candidates retain the last accepted geometry
and expose the reason in Issues. `ITERATION_LIMIT` alone remains a warning for usable
output. The low-level native relaxation adapter and application share this acceptance
policy. Strict crossing diagnostics remain available separately.

`tissue.crop(target, changes)` accepts `enabled`,
local `origin`/`normal` and `positive` half-space settings. Cropping acts in base material
coordinates after intrinsic deformation; its edges are neither attachments nor new
zero-inflation boundaries. It currently supports qualified muscle-grid modes. Incoming
surface attachments lock changes to crop topology. A fully excluded result is valid empty
geometry, but cannot supply an anatomical attachment surface. See the
[0.2.2 specification](specification_022.md) for the complete release contract.

`consumer.make_independent(entity=tissue_id)` copies its complete attached construction
graph once and returns the new source ID. Internal junctions and branch part identities
are remapped together; external anatomical targets and ordinary parents remain explicit.
Accepted geometry stays available, including Manual sources with pending authored edits.
The same command still accepts `entity` and `curve` for primitive/surface consumers.

## Curve surfaces

- `surface.preview(curves, **creation_settings)` evaluates initial correspondence without
  creating a document object. `surface.preview(target=existing_surface)` previews Realign.
  `surface.preview.status()` reports token/state/alignment; `surface.preview.accept(token)`
  installs the complete result in one undo step. `surface.preview.cancel()` releases it.
  Source edits or parent-frame changes invalidate acceptance. Candidates are excluded from
  saves and picking. This is optional API functionality, not a required desktop step.
- `surface.create(curves, kind="LOFT", name="Surface", parent="", owner="", **settings)`
  consumes an ordered list of generic curves/fibers and returns an asynchronous job ID.
  `PATCH` requires exactly one closed source; loft sources must agree on closure.
  The desktop Patch / Surface icon chooses PATCH for one selected curve and LOFT for
  two or more, using these same operations and validation. Closed lofts create directly
  in one undo action; Realign is available afterward.
- `surface.update(target, **settings)` edits `exact`, `strips`, `patch_resolution`,
  `close_across`, `flip` or `name`. Exact sampling retains evaluated corners. `strips=0`
  retains density fitted at creation/Realign; a positive count selects fixed subdivisions.
- `surface.source(target, curve, **settings)` edits per-consumer `mode`, `reverse`,
  `start`, `span` and `samples`. Transform-mode switching preserves visible placement.
- `surface.order(target, curves)` reorders every source exactly once, retaining its
  correspondence. `surface.realign(target)` asynchronously rebuilds closed direction/start
  and fitted density in one undo action. Ordinary deformation never realigns silently.
- `consumer.make_independent(entity, curve)` works for surfaces and primitives. It copies
  authored points/resources, remaps correspondence identities, and preserves accepted output.
- Generic object transforms, parenting, update modes, inspection, evaluation and deletion
  apply. Referenced source deletion is blocked; deleting the surface preserves all sources.

These commands share the desktop Construction menu and inspector policies. Accepted meshes
remain visible on pending/failed calculation; Issues expose failure and explicit recalculation.
Primitive loft boundaries share the highest effective requested count; each body piece uses
its source reference's count. Defaults remain inherited until explicitly overridden.

`surface.sources(target, curves)`, `surface.source.add(target, curve, index?)` and
`surface.source.remove(target, curve)` manage live sources while preserving existing settings
and correspondence. Removed sources remain in the document. For branched assemblies, remove
branches before changing main source order or membership.

`surface.branch.add(target, boundary, curves)` connects open branch curves through explicit
junctions on an outer main boundary. Roots must be ordered, interior and nonoverlapping;
closed/nested branches are rejected. `surface.branch.remove(target, branch)` preserves source
curves. Making a branched consumer independent copies its complete source/junction assembly.

### Direct branched construction

`curve.branch.create(source={curve, point}, points=[{position, ...}, ...],
name="Branch curve", owner="", engine="BEZIER", closed=false)` creates an ordinary curve
with world-space authored points. Its first position is resolved from the chosen existing
authored control, and its junction is created/reused atomically. The source must be editable
in the active workspace; native source frames and accepted Fiber inputs remain authoritative.
The operation preserves the source shape and forms one undo action. Cancellation before
submission is presentation-only. Regular `curve.create` behavior is unchanged.

`surface.grouping(curves=[...])` inspects two or more ordered curves without mutation,
returning `ambiguous`, named `curves`, and a suggested `plan` with `main` and `branches`.
Each branch is `{boundary: curve_id, curves: [...]}`. `surface.create(kind="AUTO", curves=[...])`
creates a patch for one closed curve, an ordinary loft for unconnected compatible curves,
or an inferred branched loft. Ambiguous connections require the explicit `grouping=plan`
argument; no provisional surface is published. A caller may edit the suggested grouping;
the complete selected source set and existing branch restrictions are revalidated.
All-Fiber source sets produce a Membrane through the same operation and evaluator.

### Tissue part and side operations

`tissue.inflation(target, changes, part="main", side="a")` edits one accepted material
part and side. Inactive mode settings remain authored. First Section Profile activation
initializes from the effective amount unless explicit profile settings are supplied.
`tissue.profile.reset` and `tissue.control.reset` accept the same target/part/side keys.
`tissue.side.copy(target, source, destination, part="main", all_parts=False)` copies the
entire inflation and height-smoothing side between opposite `a`/`b` sides. The selected
part must be accepted; all_parts includes current parts, preserves inactive historical
parts and does not alter connectors or construction. Shared topology/capability policies
apply. `tissue.profile.scale(target, factor, part="main", side="a")` proportionally scales
four depths through the native parameter adapter; factor is finite/nonnegative and all
results must remain within 0..10 m. Other profile settings are preserved. Both commands
use ordinary edit transactions and undo. `tissue.profile.scaled(profile, factor)` is a
read-only parameter transformation for previews; it returns owned profile values without
changing the document. The desktop Overall depth control uses this same transformation.
`tissue.connector(target, part, width, fullness)` edits one branch connector. All use
normal shared transactions and topology/capability validation.

`tissue.smoothing(target, changes, part="main", side="a")` configures `mode` (OFF/HEIGHT),
`radius`, `strength` and `maximum_change` for muscle grid inflation. Unsupported mode
combinations fail shared validation. Accepted rest diagnostics include part/side, fixed
sample count, KKT residuals and solver duration; they are separate from relaxation reports.
## Surface placement modes

Preview picking reads the original accepted surface. Confirmed surface placement uses
an in-memory exterior query mesh; buried and sealed-cavity faces and temporary closure
are not selectable. Attachments retain original source triangle/material coordinates.
Existing deformation resolves those coordinates without automatic nearest-surface rebinding.
Confirmed queries retain the original mesh when native qualification proves that its
topology, exposure, orientation and material correspondence already satisfy these rules.
Otherwise the existing Boolean cleanup runs. This is automatic and lazy for the requested
source/backing revision; no command, project setting or authored geometry changes.

`drawing.project` accepts `mode="PREVIEW"` (default) or `"CONFIRMED"` and role-aware
surface references. This explicit numerical query is synchronous. Desktop gestures use
coordinator jobs instead: `surface.snap.curves`, `surface.snap.points`, and
`cursor.place.surface`. `curve.create`, `curve.branch.create`, and `curve.draw` may carry
owned `projection={targets, queries}` intent; each query row is ray origin XYZ, direction
XYZ, offset, and hit flag. Unsnapped samples remain unchanged. Completed confirmation is
part of the initiating undo step; a newer authored curve edit supersedes pending placement.

## Application preferences (0.2.3)

`preferences.get` returns `routing_backend`, `path`, and any loading `error`.
`preferences.set` accepts `routing_backend: "CUSTOM" | "PIQP"` and returns updated state
after persistence. These are runtime operations: no document revision, undo entry,
recalculation or checkpoint change. The choice applies at future dispatch, including
routed Fibers and conversion previews. Running jobs and accepted results remain unchanged.
`evaluate` explicitly requests fresh calculations.

```json
[
  {"operation":"preferences.get"},
  {"operation":"preferences.set","arguments":{"routing_backend":"PIQP"}}
]
```

Use `ANTHROFORGE_PREFERENCES_PATH` for isolated automation, or inject
`Session(preferences=PreferenceStore())` for an in-memory embedded session. The CLI
loads the same user preferences as desktop without Qt. See [the contract](specification_023.md).

## Read-only tissue inspection (0.2.3)

Desktop: select a tissue and open **Inspect tissue**. Choose the displayed accepted stage,
an optional reference, and **Overlay** or **Displacement**. **Explain a surface point**
arms one-click inspection; **Check geometry** runs detailed advisory checks on demand.
Selecting a spatial finding frames and outlines its triangles. Dashed yellow x-ray guides
remain visible through occluders. These actions do not edit anatomy or create undo entries.

| Operation | Arguments and result |
| --- | --- |
| `tissue.inspect.stages` | `target`; available base/rest/intrinsic/final resources, accepted result provenance and frames. Point/curve bases retain their native presentation. |
| `tissue.inspect.compare` | `target`, `stage`, `reference`; starts a read-only background comparison. Surface stages must share material correspondence. |
| `tissue.inspect.point` | `target`, `stage`, `triangle`, `weights` (three barycentric weights); optional `expected_asset` rejects a stale displayed pick. Starts background point/constraint inspection. |
| `tissue.inspect.status` | `kind: "comparison" \| "point" \| "stacking" \| "paint" \| "section"`; lifecycle state, job, error and report. |
| `tissue.inspect.cancel` | Optional `kind`; cancels inspection and releases its retained result. |
| `tissue.inspect.check` | `target`, optional `stage="final"`; enqueues `tissue_geometry.v1` for this stage only. Read results with `issues.query`. |

Comparison statistics are vertex-weighted world-space displacement magnitudes in metres,
using canonical identities or retained material coordinates, never nearest-surface matching.
Blue → yellow → red spans zero to the report maximum; it is not an absolute shared color scale.
When comparing against a base, display the inflated stage and select the base as reference:
one base sample can have several inflated sides, so reverse matching would be ambiguous.
Different accepted construction revisions fail explicitly. Desktop displacement refreshes
after new accepted geometry; headless clients explicitly request another comparison.

Point reports include local position, material source position, delta, normal, part/side,
source boundary/seam contributions, retained zero-height rest samples, structural backing,
and native evaluated region core/feather/strength/target-reference information. Constraints
come from the settings of the accepted stage, not pending authored edits. This explains
constraint inputs, not an inverse decomposition of solver forces. Source navigation describes
current construction relationships; it is not historical evidence of each source's influence.

Geometry checks detect degenerate triangles and transverse self/other-surface crossings,
with original triangle IDs, assets, accepted/document revisions, world frames and bounds.
Self pairs sharing a vertex and touching/coplanar contact are excluded. Containment and
penetration depth are not measured. Checks stop at 512 findings and report truncation.
**Self-intersections remain allowed.** Checks never repair or replace accepted geometry.
Changed inputs mark evidence stale; no expensive automatic rerun occurs. "No findings"
applies only to the stated checks/revision, not to a general collision-free certificate.

`inspection.export` additionally accepts `tissue={stage,reference,mode,finding?}` with a
selected tissue. It freezes the stage view, a current point explanation and optional current
Issue identity, then renders that exact document snapshot in the isolated renderer. The
`.afinspection.zip` includes matching `image.png` and `inspection.json`. Native handles and
comparison buffers are temporary presentation resources, excluded from project files.

### Stacking, painting, sections and route evidence

| Operation | Arguments and result |
| --- | --- |
| `tissue.inspect.stacking` | `target`, `other`, optional `side="a"`, `other_side="a"`; production support polygons/lines, active support, accepted order, assets and frames. Rejects pending plans. |
| `tissue.inspect.paint` | `target`, `name`, `stage`, `view`, `samples`, `brush`; optional displayed `expected_asset` and `obstacles=[{asset,frame}]`. Starts a read-only colored field preview; its completed job token can commit the computed field. |
| `tissue.field.paint.commit` | `job`; commits a current completed paint preview as one undo action. Stale/cancelled tokens are rejected. |
| `tissue.inspect.section` | `target`, `stage`, optional `reference`, world `plane=[nx,ny,nz,d]`; optionally explicit displayed `surfaces=[{owner,stage,asset,frame}]`. Returns bounded contours and truncation/coplanar counts. |
| `curve.inspect.route` | `target`, optional `cold=false`; separate diagnostic calculation with current dispatched preferences. Does not publish geometry. `cold=true` bypasses warm continuation to include planning. |
| `curve.inspect.status` | No arguments; state/job/error/report for the route diagnostic. A completed diagnostic can describe a failed route: inspect `report.success` and `report.error`. |
| `curve.inspect.cancel` | Cancels/releases route diagnostics. |

Paint `view` is camera origin/right/up/forward (XYZ each), pixels per unit at depth one,
and perspective flag. Samples are a screen-space XY polyline centered on the viewport,
Y upward. `brush=[radius_px,weight,strength,falloff_power,paint_through]`; weights/strength
are 0–1. The default desktop brush affects visible samples; Paint Through is explicit.
Base fields map through thickness; Rest fields retain their own material domain. Stroke
coverage is based on the entire polyline and starting weights, not pointer event count.

Constraint point reports additionally contain world-space `goal`, `actual`, `residual`,
and `goal_basis` for influencing regions. Source-relative goals use accepted rest data;
target-relative goals resolve the retained binding against **current accepted targets**.
They are not historical solver-force evidence. Unavailable goals report `goal_error`.

Section planes keep `n·p+d >= 0`; no anatomical geometry is capped or replaced. Desktop
section scope defaults to the selected tissue and comparison stages, with an explicit
surrounding-geometry switch. Picking skips discarded intersections and returns original
triangle IDs/material locations from the same displayed mesh.

Route records identify Reference, Planner, Solver seed, Solver trial and Final, plus span,
attempt, trial, accepted iteration count and termination. Coordinates are world metres.
Contacts contain edge/collider/face/feature/contained/limiting/factor/gap, path XYZ,
surface XYZ and normal XYZ. Limits are 128 complete path records, 131072 points and 4096
contacts. `omitted` reports overflow; a final record may be unavailable when the limit is
reached. The desktop displays at most 8192 points/512 contacts per selected record and
labels that additional viewport limit. A missing planner stage during warm continuation
is expected. Diagnostic capture is not performed during ordinary solves.

`inspection.export` accepts `route={index,showContacts}` for a selected routed curve/Fiber;
the frozen report includes the captured trace and restores its selected step without
rerouting. Tissue exports also preserve current stacking/paint evidence and optional
`tissue.section={enabled,target,axis,position,flip,cut,wholeScene}` presentation.
Camera persistence does not invalidate these geometry diagnostics. Authored/accepted scene
changes invalidate their conservative input signatures. API callers supply visible occluders
for visible-only painting; the desktop captures them from the displayed scene automatically.

## Editable Shrinkwrap and Segment Chain

`primitive.create(kind="SEGMENT_CHAIN", name?, parent?)` creates a parameter-driven
SCP without a hidden curve or imported source. `chain.segment(entity, index, length?,
radius?, bend?, samples?, sides?)` edits one segment; `chain.resize(entity, count)`
sets 1–32 segments. `chain.configure(entity, spread?, bend_mode?, profile?, unite?)`
edits shared settings. Angles use radians in the API and degrees in the inspector.
`ADJACENT` uses each bend plus its predecessor; `CUMULATIVE` sums preceding bends.
Zero length disables a segment; radius zero is permitted only for a disabled segment.
The AUTO radius profile is flattened position/scale pairs, spanning 0–1.

`shrinkwrap.add(target, surface, offset=0, mode="ON_SURFACE")` returns a binding ID.
`target` uses the common owner/stage/component reference; `surface` is an SCP ID or
an explicit `{target, role}` surface reference, including available tissue roles.
`shrinkwrap.update(binding, surface?, offset?, mode?)` retains common lifecycle,
ordering, enabled/strength/weight settings and deletion protection. Nearest-surface
modes are `ON_SURFACE`, `INSIDE`, `OUTSIDE`, `OUTSIDE_SURFACE`. Offsets are in target-local
units, matching the qualified Blender behavior. Project/nearest-vertex/target-normal
projection are not implemented by this adapter; it never substitutes them silently.

`modifier.add(entity, kind="SUBDIVISION", levels=1)` adds linear subdivision (0–5).
`modifier.add(entity, kind="DISPLACE", offset=[x,y,z])` adds local vector displacement.
Use `modifier.update(binding, levels? / offset?)`, normal deformer ordering/removal,
and `body.update(..., subdivision=...)` for pre-bend base refinement.
Quad Simple subdivision matches the Blender fixtures; higher-level nonplanar n-gon
Simple evaluation is not claimed equivalent. All stages remain editable, never baked.

Changing union connectivity retains material attachment provenance. A location covered
by a new union fails explicitly instead of rebinding. Indexed/weighted geometry
membership on Segment Chain is unavailable; use whole-target deformation or a lattice
with stable cage-point memberships. `evaluate` splits attachment work across intervening
geometry dependencies so complete assemblies do not wait on their own batched poses.
The returned ID identifies the final submitted pose batch; use `wait` to await all work.
See `examples/segment_chain.json` for a portable shared-API workflow.


### Retained material correspondence for authored open lofts

`surface.correspondence(target, mapping, across)` installs explicit correspondence
for an open ordinary or branched Surface or Membrane. `mapping` maps each source curve ID to
ordered `[point_id, station]` pairs, including both endpoints. Stations are finite,
strictly increasing and start at zero; their final value is normalized by the native
adapter. For ordinary lofts, `across` supplies one retained insertion count per
adjacent curve pair. For branches use `across=[]`: connector sampling retains its
existing shared-seam rules, while main and branch curves use their authored stations.
This operation is useful when reproducing an authored material loft whose sections
must not move with changing curve arclength. It uses normal topology locks, undo,
dependency evaluation and resource ownership. It does not import a Blender file.

Stable point IDs survive deformation, persistence and Make Independent. Native
sampling interpolates additional evaluated points without dropping corners. Removing
a referenced station fails explicitly and retains the previous result. **Realign**
resets this explicit mapping. Closed curves, partial source ranges and uniform sampling
require resetting correspondence first; there is no silent
replacement with another interpretation. Default loft authoring is unchanged.
Adding a branch to an already mapped ordinary loft still requires explicit Realign;
configure the complete assembly's correspondence after establishing its junctions.
## Shortcut inspection (0.3.1)

Read-only `shortcut.effects`, `shortcut.formulas`, `shortcut.attachment_policy` and
`shortcut.progress` expose influence, captured numerical evidence, effective policy and
downstream readiness without edits. See [operation signatures and walkthrough](shortcuts_031.md).
