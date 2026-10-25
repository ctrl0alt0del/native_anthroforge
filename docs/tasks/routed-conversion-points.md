# ROUTED conversion point preference

- Task branch: `codex/routed-conversion-points`
- Integration branch: `main`
- Starting revision: `4ff1ef8`
- Status: pending full validation
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

Implemented persistent preference, direct desktop choice and shared guide selection for
direct/configured/Parametric engine switches and optional previews. Explicit preview lists
override the preference. Closed paths retain all points; mandatory binding/junction points
remain. Existing ROUTED settings edits do not remove controls. Point reduction updates
consumer material stations for retained identities in the same undo action. Topology locks
remain enforced. Native solver and attachment behavior were not changed.

## Verification

42 focused conversion/preference tests pass, plus architecture checks. Ruff and mypy pass.
`tools/preferences_acceptance.py` passes offscreen: both choices, persistence, no document
edits, backend selection and future Fiber dispatch. Preferences screenshot inspected;
no QML warnings. No desktop takeover or interactive acceptance claimed.

Read-only local SCM probe on `build/scm-ribs-distortion/after.anthroforge` (Ribs radius 3):
all three SCM Fibers convert from 73 points to two, retaining exact stored bindings;
all three paths, membrane and Tissue finish ready. Evidence:
`build/routed-conversion-points/scm.json` and `scm.afprofile.zip`. Source project not saved.
This establishes conversion/lifecycle success, not an improved solver or anatomical fit.
Development gate is running in `build/routed-conversion-points/development-gate.log`;
native build and all five native CTests passed. Full gate and package checks pending.

## Next actions and blockers

1. Complete development gate, inspect SCM output and package the existing canonical version.
2. Check packaged preference and conversion workflows, then integrate the validated branch.

## Recovery inputs

Existing local `.venv`; native library/build infrastructure unchanged. SCM case snapshots
remain under ignored `build/scm-ribs-distortion/` and are not source deliverables.
