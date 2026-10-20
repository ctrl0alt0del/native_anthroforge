# Direct curve engine selection

- Task branch: `codex/direct-curve-engine`
- Integration branch: `main`
- Starting revision: `b2d3be74fb0ef5b719e9605d0bfc840becfd1870`
- Status: implemented and qualified; final integration pending
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat

## Outcome and decisions

Replace the desktop Change path engine / Preview / Accept workflow with a visible
engine selector. Selecting an engine applies it directly as one undo action.
The user explicitly chose retaining existing authored control points and letting the
engine define the path; do not resample solved output into new control points.

The user also establishes a permanent UI/UX rule: minimize steps to the outcome, and ask
when the intended interaction is unclear. Recorded in AGENTS.md and engineering_guidelines.md.
This supersedes mandatory preview conversion in earlier specifications and task records.

## Ownership and invariants

Use a shared document command, ordinary authored revisions, dependency invalidation and
the current task coordinator. Do not implement direct selection by silently clicking through
the old preview API. Retain point identities, handles, junctions and Fiber bindings; use
resolved authored points for Fiber edits. Preserve topology/workspace restrictions,
pending Manual results, obsolete-job rejection, failure retention and single-action undo.
The optional existing headless preview API can remain separate from the direct UI.

## Implemented checkpoint

- `curve.engine` installs a typed engine through ordinary transactions, shared topology
  policy, invalidation and path scheduling; same-engine selection is a no-op. Keeps existing
  points and uses resolved authored Fiber state. No preview job is involved.
- `CurveEngine.qml` is directly visible for a standalone Curve/Fiber, also available for
  a primitive's selected source while editing. Removed the old conversion gate. User
  activation alone writes; undo/refresh/rejected edits restore the authoritative selection.
- Updated API, specifications, architecture, walkthrough and existing QML qualification tools.
- 24 focused tests passed (engine, optional conversion, Fiber conversion and architecture).
  Ruff/mypy passed. Offscreen actual saved project passed: Curve/Fiber routing clearance,
  retained points, one-action undo/redo, direct selection without edit mode, primitive
  source selection, shared topology lock/rejection/reset/unlock. Existing obstacle and
  Fiber editing QML checks passed. Offscreen capture verifies layout, not 3D rendering.
- The 120-point/120-obstacle workflow passed interaction assertions but its full stress
  profiler recording evicted events and overflowed the Qt queue. The tool now explicitly
  reports this bounded-capture loss; no complete timing totals are claimed. Rerun passed:
  177,813 evicted events and 143,291 Qt drops are explicit in the incomplete capture.

## Final qualification and delivery

- Full Windows gate: 1,304 pytest cases passed (732 existing Qt deprecation warnings,
  86.70 seconds); three native CTests, style/function limits, Ruff/format, mypy, numerical
  imports and doctor passed. The first native link attempt overlapped a dev-DLL GUI check
  and was denied by Windows; serializing that shared resource resolved it.
- Clean tracked runtime source: `e2aef15db8a2a6b60374822025953e44755b88ab`.
  Minimal-PATH portable suite passed. A separate packaged command test switches both
  objects in the actual project copy, checks undo, saves/reopens, verifies retained
  point IDs/positions and zero curve/cube segment intersections, and renders revision 312.
- Inspected offscreen control screenshots and the packaged hidden-GPU image. No OS input,
  visible windows or hands-on acceptance was performed. Original fixture SHA-256 unchanged.
- Qualified package installed at the sole canonical `dist/0.2.2/AnthroForge.dist`, after
  verifying both installations were closed. Prior installation retained under this task's
  ignored build directory. Executable SHA-256:
  `cfbe450eedeeacc1fe9e4ebc82407ab9ab1736869934189582328080affdf121`.
- Separate ownership review: the UI performs no conversion orchestration/numerical work;
  shared validation and ordinary edits/coordinator own policies and lifecycle. No new
  scheduler, preview workaround or duplicated Fiber path implementation was added.
- Remaining final delivery: commit/push this qualification record, merge/push main,
  refresh shipped documentation and the single companion source archive, verify bytes.

## Recovery inputs

User fixture: `E:/development/WIP_models/solver_doesnt_work.anthroforge` (read only).
Temporary evidence: `build/direct-curve-engine`. Preserve unrelated root `__init__.py`.
Relevant files: application/curve_edit_operations.py, application/commands.py,
desktop/qml/PrimitiveInspector.qml and CurveEngine.qml.
