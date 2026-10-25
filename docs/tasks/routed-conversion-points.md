# ROUTED conversion point preference

- Task branch: `codex/routed-conversion-points`
- Integration branch: `main`
- Starting revision: `4ff1ef8`
- Status: in progress
- Last updated: 2026-10-25 Europe/Bucharest
- Active writer: desktop

## Outcome and acceptance

Add persistent Preferences choice for switching a curve/Fiber to ROUTED: endpoints
(default) or all authored points. Closed curves retain all points, confirmed by user.
Apply at conversion time only; retain genuine anatomical bindings, shared junctions,
topology locks, ordinary transactions, undo/redo and headless/desktop parity.
No numerical solver changes or automatic conversion of existing projects.

## Decisions and relevant files

Extend core Preferences and existing atomic preference storage; shared conversion policy
owns point selection, with explicit conversion point lists remaining authoritative.
Desktop adds a direct choice in the existing Preferences dialog. Keep existing solver
backend preference independent. Computation history and API documentation must describe
the changed conversion default and closed-curve exception.

## Current state

Existing direct engine switches retain all authored points, including migrated dense
Free fibers. Native ROUTED treats them as hard constraints. SCM experiments demonstrated
unbound interior Spine contact prevents conversion before optimization. Existing
conversion preview already supports explicit point subsets and mandatory-point checks.
Investigating retained Fiber capture and surface correspondence before reducing points.

## Verification

Pending implementation, relevant contract tests, development gate and offscreen Preferences
inspection. User desktop must remain untouched. Preserve unrelated root `__init__.py` and
isolated SCM experiment branch; no experimental kernel promotion.

## Next actions and blockers

1. Implement preference, shared conversion policy and desktop control.
2. Test curves/Fibers, closed paths, junctions, attached consumers, undo and persistence.
3. Run development checks, inspect offscreen UI, checkpoint and validated integration.

## Recovery inputs

Existing local `.venv`; native library/build infrastructure unchanged. SCM case snapshots
remain under ignored `build/scm-ribs-distortion/` and are not source deliverables.
