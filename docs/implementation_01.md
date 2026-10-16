# AnthroForge 0.1 implementation contract

Implement the approved imported-SCP assembly editor. The full product decisions
in standalone_application_recommendations.md remain authoritative.

## Release capabilities

- OBJ, ASCII/binary STL and PLY import, one independent SCP per file; explicit units.
- Immutable canonical polygons, derived render triangles, accurate native picking.
- Single-root hierarchy, empty groups, rename/duplicate/delete/reparent and TRS.
- Complete SCP attachment modes, locks, rotation strategies, recapture, origin move,
  global freeze/rebind and Live/On Release/Manual updates.
- Shared document API, transactions, undo/redo, revision-qualified background jobs.
- Exact historical save checkpoint, blocked-save policies, portable project storage.
- Document-backed desktop, named focused workspaces, activity and diagnostics.
- Headless operations and revision-matched inspection; portable Windows distribution.

## Explicit exclusions

Native curve primitives and separate deformers move to [0.1.2](primitives_012.md),
superseding the earlier 0.1.1 allocation. Linked mirroring, project merging, legacy conversion,
fibers, muscles, tissues, skin and topology are later milestones. No geometry export
is available until skin construction exists. No persisted undo or crash recovery.

## Implementation and acceptance order

1. Document/history/scheduler/storage with overlap, queue, undo and failure fixtures.
2. Import and native queries with cube.obj and ordinary format variants.
3. Addon-parity attachment capture/propagation and controls.
4. Desktop/headless complete workflows and measured publication/picking.
5. Relocatable Windows package, licenses and reproducible walkthrough.

Completion requires integrated, visually inspected editing, saving/reopening and
headless parity. A compiling scaffold or isolated algorithm test is insufficient.
30 FPS, 50 ms input and 100 ms cancellation acknowledgement remain soft targets.
