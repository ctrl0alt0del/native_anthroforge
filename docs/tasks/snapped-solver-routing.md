# Solver behavior on snapped curve and fiber

- Task branch: `codex/snapped-solver-routing`
- Integration branch: `main`
- Starting revision: `248cc66f62684c7218253335777aaf75f2e20949`
- Status: investigation in progress
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat

## Outcome and acceptance

Investigate the user's saved snapped curve/fiber, reproduce the expected surface route,
and correct any demonstrated runtime or editing defect at its owning boundary. Preserve
the original file and unrelated root `__init__.py`. Use background-only validation.

## Observed evidence and contracts

The supplied schema-4 project contains one unit cube, a two-point Curve, and its independently
bound Fiber copy. Both saved engine settings are BEZIER, resolution 24. Both accepted paths
are ready without routing diagnostics. This establishes that the saved objects have not
accepted routing conversion; it does not establish why the user's workflow left them so.

Per specification_020.md and specification_021.md, snapping and anatomical binding do not
silently change the path engine. Conversion is explicit, previewed and undoable; a Fiber
preserves its copied engine. Check conversion on these exact coordinates before drawing
conclusions about native solver correctness or the UI.

## Verification and next actions

1. Run explicit ROUTED previews on the saved Curve and Fiber; inspect accepted geometry.
2. Inspect the actual conversion controls and their selected/accepted engine presentation.
3. Correct a demonstrated defect, then validate the affected API, GUI and packaged workflow.
4. Record evidence, checkpoint and integrate only completed work.

## Recovery inputs

Original: `E:/development/WIP_models/solver_doesnt_work.anthroforge`.
Local-only evidence: `build/snapped-solver-routing`.
Relevant owners: `desktop/qml/CurveConversion.qml`, application conversion operations,
`application/routing_evaluation.py`, and `native/src/routing*.cpp`.
