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

## Verification and next actions

1. Add the direct shared engine operation and tests for state, undo, async work and policies.
2. Replace conversion controls with a direct selector and qualify background QML behavior.
3. Align active documentation, run the development gate and packaged checks.
4. Replace only the canonical 0.2.2 distribution after it closes, archive source and merge/push.

## Recovery inputs

User fixture: `E:/development/WIP_models/solver_doesnt_work.anthroforge` (read only).
Temporary evidence: `build/direct-curve-engine`. Preserve unrelated root `__init__.py`.
Relevant files: application/curve_edit_operations.py, application/commands.py,
desktop/qml/PrimitiveInspector.qml and CurveConversion.qml.
