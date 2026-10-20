# Solver behavior on snapped curve and fiber

- Task branch: `codex/snapped-solver-routing`
- Integration branch: `main`
- Starting revision: `248cc66f62684c7218253335777aaf75f2e20949`
- Status: fixes implemented; full gate and packaged delivery pending
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
synchronizes to the selected object's actual engine, including undo/redo and selection
changes. Background full-QML qualification on the original project passes.

Explicit conversion revealed a separate numerical defect on these exact inputs: no sampled
point is interior, but the first/last segments cross the cube near the pins. The independent
path collision checker reports segment 0. Native trace shows the planner initially accepts
the direct chord, its subdivided handoff fails, and SQP's owner-contact exemption permits
an invalid result. The cause was the graph search's separate edge checker: it bypassed
the planner's solid-interior owner-chord rejection. It now calls the existing shared
`clear` policy. No new solver, Python geometry loop or migrated kernel change is needed.

Rejected experiment: removing adjacent-edge expansion from owner_span made conversion
fail and changed four existing parity cases. Those changes were reverted. Do not treat
an increased iteration budget or a successful solver return as geometry acceptance.

Per specification_020.md and specification_021.md, snapping and anatomical binding do not
silently change the path engine. Conversion is explicit, previewed and undoable; a Fiber
preserves its copied engine. Check conversion on these exact coordinates before drawing
conclusions about native solver correctness or the UI.

## Verification and next actions

28 focused routing/architecture tests pass, including exact user pins, bound/unbound
contacts at 32/64/128 samples, warm continuation and independent whole-segment checks.
The original donor bound-box output fails that check; its corrected output passes.
This intentional geometry correction is documented in native/migration/README.md.
All other donor/skull cases remain numerically identical. Temporary diagnostics removed.

Full-QML `tools/snapped_routing_acceptance.py` passes on the original project, exercising
selection/preview without document edits, explicit application, curve/fiber independence,
undo/redo, selector synchronization and cancellation without QML warnings. Captures inspected;
this offscreen platform does not render the 3D scene. Separate hidden-GPU captures cover shape.

1. Run the full development gate and existing routing GUI checks.
2. Package and qualify in an ignored build directory while the user's installed app runs.
3. Deliver the corrected separate project and replace the canonical build after it closes.
4. Update evidence, merge and push the validated task.

## Recovery inputs

Original: `E:/development/WIP_models/solver_doesnt_work.anthroforge`.
Local-only evidence: `build/snapped-solver-routing`.
Relevant owners: `desktop/qml/CurveConversion.qml`, application conversion operations,
`application/routing_evaluation.py`, and `native/src/routing*.cpp`.
