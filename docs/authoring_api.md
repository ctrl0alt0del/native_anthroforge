# Local authoring API, version 0.1

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
| scp.delete | entity | Delete its subtree |
| scp.reparent | entity, parent | Preserve pose, change relation and capture |
| scp.attachment | entity and any settings below | Change/capture attachment |
| scp.recapture | entity | Queue capture from the current pose |
| scp.origin | entity | Move origin to captured anchor while preserving mesh position |
| attachments.enable | enabled | Freeze/rebind all attachments |
| update_mode | mode; optional entity | LIVE, ON_RELEASE, MANUAL; per-SCP also INHERIT |
| begin / commit / cancel | none | One editing transaction |
| undo / redo | none | Navigate authored history |
| evaluate | none | Queue explicit attachment update |
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

Attachment settings:

- parent_mode: SURFACE_NEAREST or OBJECT_ORIGIN.
- child_mode: FACE_CENTER, VERTEX_NEAREST or OBJECT_ORIGIN.
- strategy: AUTO, STABLE_SURFACE or DEFORMATION_FLOW.
- follow_rotation: boolean.
- face_lock and vertex_lock: canonical zero-based indices, or -1 to clear.

Workspace settings include name, members (SCP IDs), focused, hidden, unpickable,
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
