# Direct curve engine selection

- Task branch: `codex/direct-curve-engine`
- Integration branch: `main`
- Starting revision: `b2d3be74fb0ef5b719e9605d0bfc840becfd1870`
- Status: implementation in progress
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
  reports this bounded-capture loss; no complete timing totals are claimed. Rerun pending.

## Verification and next actions

1. Run the development gate, rerun the updated stress check and inspect hidden GPU output.
2. Qualify the packaged executable, including the same direct command and updated QML.
3. Replace only the canonical 0.2.2 distribution after it closes, archive source and merge/push.

## Recovery inputs

User fixture: `E:/development/WIP_models/solver_doesnt_work.anthroforge` (read only).
Temporary evidence: `build/direct-curve-engine`. Preserve unrelated root `__init__.py`.
Relevant files: application/curve_edit_operations.py, application/commands.py,
desktop/qml/PrimitiveInspector.qml and CurveEngine.qml.
