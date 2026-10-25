# ROUTED conversion point preference

- Task branch: `codex/routed-conversion-points`
- Integration branch: `main`
- Starting revision: `4ff1ef8`
- Status: complete
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

Focused conversion/preference tests pass, plus architecture checks. Added coverage verifies
an interior anatomical binding remains mandatory. Ruff and mypy pass.
`tools/preferences_acceptance.py` passes offscreen: both choices, persistence, no document
edits, backend selection and future Fiber dispatch. Preferences screenshot inspected;
no QML warnings. No desktop takeover or interactive acceptance claimed.

Read-only local SCM probe on `build/scm-ribs-distortion/after.anthroforge` (Ribs radius 3):
all three SCM Fibers convert from 73 points to two, retaining exact stored bindings;
all three paths, membrane and Tissue finish ready. Evidence:
`build/routed-conversion-points/scm.json` and `scm.afprofile.zip`. Source project not saved.
Actual SCM final geometry was inspected from two fixed cameras (`scm.png`), without saved
presentation changes. This establishes conversion/lifecycle success, not an improved solver
or anatomical fit.
Development gate components passed: lock, Ruff, formatting, mypy (407 modules), native
build, five native CTests, configured native/script style, 2,114 Python tests, numerics
imports and native doctor. Initial `tools/check.ps1` run exposed two legacy adaptive-route
fixtures assuming three retained controls; they now explicitly select ALL_POINTS. The
focused regression and complete pytest suite were rerun successfully after that test-only
correction. Evidence: `development-gate.log`, `pytest-final.log`, `numerics.log`, `doctor.log`
under `build/routed-conversion-points`. Existing Qt deprecation warnings remain.

Canonical package build succeeded at `dist/0.3.5/AnthroForge.dist/AnthroForge.exe`; the full
offscreen minimal-PATH portable suite passed. Its Preferences checks verify two controls
for ENDPOINTS and three for ALL_POINTS in the actual executable. Packaged Preferences
screenshot inspected. Runtime sources are identical to packaged checkpoint `dbfae78`;
subsequent changes are acceptance coverage and documentation. Native sources are unchanged
from the integration baseline. No new version or additional distribution was introduced.

Ownership review: shared application conversion policy selects authored guides; only
desktop presentation depends on Qt. Existing application transactions/coordinator own
history and evaluation. Consumer correspondence changes share the conversion transaction.
Native numerical algorithms, retained binding semantics and read validation are unchanged.
Unrelated `__init__.py`, unfinished 0.3.4 work and SCM experiments remain separate.

## Next actions and blockers

No remaining implementation work. Companion source archive and packaged documentation
are refreshed during delivery; branch history records the validated integration.

## Recovery inputs

Existing local `.venv`; native library/build infrastructure unchanged. SCM case snapshots
remain under ignored `build/scm-ribs-distortion/` and are not source deliverables.
