# Local authoring API, version 0.1.3

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
| save | path, blocked_policy | Saved revision/path or pending jobs |
| open | path | Load the project and queue equivalent SCP startup synchronization |
| workspace.create | name, members; optional children=false | Create and activate focused workspace |
| workspace.select | index | Activate named workspace |
| workspace.update | presentation settings below | Update active workspace without an anatomical undo step |

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
wait drains calculations; checkpoint saves the historical committed revision when blocked;
pending reports that saving is blocked without writing. Read-only background work does
not block commitment. A failed calculation is terminal and its failed state can be saved.

Use begin/update/commit for a drag-like sequence. A single editing command implicitly
creates one transaction. Manual mode needs evaluate. Do not infer calculation completion
from a returned job ID: use wait or inspect jobs. File inspection and revision-matched GPU
capture also have process-level CLI commands documented in quickstart.md.

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
| control.transform | control, values=[x,y,z,rx,ry,rz,sx,sy,sz] | Local TRS for an SCP-following or control-supported control; world TRS for document-frame or SCP-attached controls, recapturing the latter's surface/origin placement |
| control.follow | control; optional entity="" | Change follow source preserving world placement; clear local attachment |
| control.attach | control, support; optional surface=true | Bind to SCP surface/origin or another control |
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

Schema 2 embeds editable definitions, source meshes, bindings and accepted results for
the selected revision. Version-1 projects migrate on read. Native handles and undo history
are not serialized. Older application versions reject schema 2.
