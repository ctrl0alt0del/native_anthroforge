# Routed curve follows straight segments

- Task branch: `codex/solver-routing`
- Integration branch: `main`
- Starting revision: `2e8dc0b`
- Status: investigating
- Last updated: 2026-10-19, Europe/Bucharest
- Active writer: local desktop chat

## Outcome and acceptance

Investigate the user's `solver_test.anthroforge`, correct the responsible runtime or
editing boundary if defective, and qualify the actual scene in background-only checks.
Preserve the original project and unrelated root `__init__.py`. Follow the engineering
guidelines and the explicit-obstacle/ordinary-curve contract in specification_020.md.

## Observed evidence

The saved Drawn curve uses ROUTED with three authored points and no obstacles or bindings.
Its accepted result is successful and contains native solver diagnostics. Native routing
therefore received no scene surfaces. The conversion UI allows routing-point selection
but not obstacle selection; obstacles can only be selected afterward in a collapsed panel.

On a disposable project copy, enabling both existing cubes produces `Routing could not
find a collision-free path`, retaining the old accepted path. The authored points lie on
cube surfaces. Whether missing geometric contact ownership or another planner failure
causes this second result remains unverified; do not treat it as established yet.

## Next actions

1. Compare cold/warm solves and geometric contact inputs on the actual scene.
2. Fix the demonstrated owning boundary and add representative regression coverage.
3. Qualify offscreen rendering/editing, native/parity and packaged behavior, then merge.

## Recovery inputs

Original: `E:/development/WIP_models/solver_test.anthroforge`, SHA-256
`0c68966279bf8ea2444c252b3a1c4fc1cbb4551b662580d5d4fec4bf9aeb0ea5`.
Disposable inputs and experiments: `build/solver-routing` (ignored, local only).
Relevant owners: application/routing_evaluation.py, core/curve_dependencies.py,
native/src/routing*.cpp and desktop/qml/CurveConversion.qml and RoutingSettings.qml.
