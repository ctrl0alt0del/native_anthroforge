# AnthroForge 0.1 architecture

The confirmed specification remains authoritative. This implementation is an imported-SCP
assembly editor. Advanced anatomical features enter through the same core in later releases.

## Ownership and execution

- core/document.py and entities.py hold immutable SCP records, UUID identities, canonical
  metre units, attachment bindings and named workspace state. A populated SCP hierarchy
  has exactly one root; an empty document is valid.
- application/session.py owns the current revision, immutable native mesh assets, history
  and scheduler. Commands are explicit and independent of viewport selection or Blender.
- application/commands.py is the shared UI/headless catalogue. Transactions collapse
  repeated drag updates into one undo step; cancellation restores authored state.
- application/scheduler.py owns dispatch, output reservations, coalescing, priorities,
  safe cancellation, publication and save checkpoints. Jobs acquire their input revision
  at dispatch. Queued writers also block commitment; read-only jobs do not.
- Each mesh asset owns a native handle. Workers retain snapshot mesh references; published
  geometry is immutable. Canonical polygon indices remain separate from render triangles.
- Native C++ handles import/triangulation, BVHs, exact picking, transforms and attachment
  calculations. Numerical loops do not call Python per sample or iteration.

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

Undo cancels jobs whose origin/start revision leaves history. Redo restarts their work;
it does not resume a paused solver. Historical entries share immutable data and retain
revision membership. Undo history itself is not persisted.

## Presentation and persistence

Qt owns its UI objects. RenderModel publishes at most two 16,384-triangle chunks per tick.
QQuick3DGeometry owns its QByteArray buffers. Complete native meshes are prepared in workers;
the GUI publishes bounded chunks. Hover, selection and visibility do not change authored
mesh data. Picking uses one native scene call and per-mesh BVHs; no scene-level BVH yet.

Named workspaces preserve camera, orthographic mode, hidden/unpickable sets, member IDs and
independent overlays. Outside entities remain transparent/read-only while their dependencies
remain present. These presentation changes do not create anatomical undo steps.

Project files are versioned ZIP64 containers with JSON metadata and canonical NPY arrays
(allow_pickle=False). Saving writes a sibling temporary file, flushes it and atomically
replaces the target. A cooperative file lock prevents two writable application sessions.
Meshes are embedded, not external references. Loaded SCP attachments receive the addon's
equivalent startup synchronization; unrelated future solvers are not launched.

## Measurement and extension

Bounded samples record GUI ticks, frame intervals, picking, preparation, publication,
cancellation requests and safe completion. The Diagnostics overlay reports recent p95
values. tools/viewport_benchmark.py and tools/gui_acceptance.py record reproducible evidence.

JSON batch/line transports and numerical inspection run without Qt. Revision-matched image
capture starts Qt offscreen. The line server keeps scheduling while waiting for client input.
MCP, new primitive families, fibres, muscles and skin remain separate feature migrations.

Qt/PySide versions must match when rebuilding the native viewport plugin. Windows DLL
preloading intentionally ensures Python and Qt use the same geometry registry. The current
portable package contains only dependencies needed by 0.1; numerical development extras
remain available for later migrations.
