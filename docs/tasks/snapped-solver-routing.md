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

The user confirmed selecting ROUTED without Preview/Accept. The UI change now labels
the active engine, the conversion target and unapplied preview separately; its selector
synchronizes to the selected object's actual engine. Desktop qualification remains pending.

Explicit conversion revealed a separate numerical defect on these exact inputs: no sampled
point is interior, but the first/last segments cross the cube near the pins. The independent
path collision checker reports segment 0. Native trace shows the planner initially accepts
the direct chord, its subdivided handoff fails, and SQP's owner-contact exemption permits
an invalid result. The exact cause of the direct-chord acceptance is under investigation.

Rejected experiment: removing adjacent-edge expansion from owner_span made conversion
fail and changed four existing parity cases. Those changes were reverted. Do not treat
an increased iteration budget or a successful solver return as geometry acceptance.

Per specification_020.md and specification_021.md, snapping and anatomical binding do not
silently change the path engine. Conversion is explicit, previewed and undoable; a Fiber
preserves its copied engine. Check conversion on these exact coordinates before drawing
conclusions about native solver correctness or the UI.

## Verification and next actions

1. Diagnose direct-chord acceptance and restore a valid corridor for the exact saved scene.
2. Remove temporary native diagnostics; add complete segment regression coverage.
3. Qualify conversion controls, API, GUI and packaged workflow.
4. Record evidence, checkpoint and integrate only completed work.

## Recovery inputs

Original: `E:/development/WIP_models/solver_doesnt_work.anthroforge`.
Local-only evidence: `build/snapped-solver-routing`.
Relevant owners: `desktop/qml/CurveConversion.qml`, application conversion operations,
`application/routing_evaluation.py`, and `native/src/routing*.cpp`.
