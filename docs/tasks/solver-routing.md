# Routed curve follows straight segments

- Task branch: `codex/solver-routing`
- Integration branch: `main`
- Starting revision: `2e8dc0b`
- Status: implementation complete; full gate and portable qualification pending
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

Enabling both cubes reproduced failure. A cold solve rejected the unbound surface knots;
the same positions with explicit numerical contact owners succeeded. Native evaluation
now classifies unbound knots touching selected surfaces within its numerical floor. This
creates no anatomical binding, never changes explicit owners, and does not exempt inside
or merely nearby points. The existing native nearest-surface index performs the queries.

The former straight accepted path also supplied an invalid warm seed crossing the newly
selected cubes. Native continuation now checks solid-interior feasibility before reuse;
invalid seeds go through corridor planning. A feasible seed may still need clearance
restoration in SQP. Failed warm solves get one cold planning attempt; cancellation and
other errors still terminate normally. No Python numerical path or competing job exists.

One initial experiment applied full requested-clearance validation to warm seeds. That
unnecessarily rejected a valid skull continuation and broke parity. The final check
separates solid-interior feasibility from recoverable clearance, preserving all existing
21 routing/native/anatomy parity cases. Merely retrying solves marked infeasible was also
insufficient: a crossing seed could pass the solver's broad pin-contact exemption, so
independent seed validation is required. These rejected approaches are not active code.

RoutingObstacles.qml is shared by conversion and current-engine settings. Users can choose
obstacles before preview; an empty effective set has a visible notice. Automatic fiber
attachment surfaces are identified and cannot be unchecked. Typed conversion settings are
projected explicitly, avoiding Qt property-map implementation fields.

## Verification

29 focused routing/architecture tests pass, including the compact actual-user fixture,
saved warm samples, unchanged pin positions, independent intersection queries, inside/near
rejection, explicit binding preservation, undo and save. Native build/3 CTests pass.
Existing routing-editor acceptance and the new offscreen conversion/obstacle/undo workflow
pass without QML warnings. Its capture and before/after invisible D3D11 captures of the
actual project were inspected. The rerouted saved copy reports no centerline intersections
with either cube; original SHA-256 is unchanged. No visible window or desktop input used.

## Next actions

1. Run the complete development gate and review ownership/coupling.
2. Build a separate 0.2.0 solver-fix portable folder and qualify the actual saved case.
3. Deliver the executable and a distinct rerouted project copy, then merge and push.

## Recovery inputs

Original: `E:/development/WIP_models/solver_test.anthroforge`, SHA-256
`0c68966279bf8ea2444c252b3a1c4fc1cbb4551b662580d5d4fec4bf9aeb0ea5`.
Disposable inputs and experiments: `build/solver-routing` (ignored, local only).
Relevant owners: application/routing_evaluation.py, core/curve_dependencies.py,
native/src/routing*.cpp and desktop/qml/CurveConversion.qml and RoutingSettings.qml.
