# Routed conversion failure in solver_fail1

- Task branch: `codex/solver-fail1`
- Integration branch: `main`
- Starting revision: `9cc6c7cd64ae3a0090bf3f715f434378653d441f`
- Status: diagnosed; user requested approach discussion before implementation
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat, direct work

## Outcome and acceptance

Reproduce the reported failure when switching the supplied curve to ROUTED, identify
the actual rejected condition and correct the responsible implementation if defective.
Validate the original geometry and complete path, not just successful solver return.
Preserve user-authored points, original file, routing safety and retained-output semantics.
Any real authored conflict or behavior choice must be explained before choosing a repair.

## Current state

Created an isolated copy of the project under ignored `build/solver-fail1/`.
Project SHA-256: `61df6958b6d63f8974d88935007ee9d727504af1e89c1ffe252761c10f2e51b2`.
The original was not modified. Reproduced failure with the four authored points,
24 samples, 0.002 m clearance and 64 accepted steps.

The planner and solver disagree on sampling allocation. `routing_handoff.cpp`
constructs and validates a 24-point corridor preserving its bends, with per-span
counts 8/10/8 (shared endpoints counted once). `routing_planner.cpp::prepare_routes`
then calls uniform `resample` to fit the separate straight-chord reference allocation:
7/13/6. That second sampling discards required corners and cuts through both cubes.

Independent `af_path_collisions` checks on the actual captured buffers:

| Buffer | Total points | First colliding segment per cube |
| --- | --- | --- |
| Validated handoff | 24 | -1, -1: clear |
| Resampled solver seed | 24 | 3, 20: intersects |

Collision tolerance: `3.2211166569453247e-9` m. The valid 24-point handoff proves that
this fixture does not need more samples simply to represent a clear path.
Isolated spans solve; whole-curve 16/24/32/64-sample probes fail, while 128 succeeds.
Those probes diagnose sampling sensitivity and are not a proposed settings workaround.

Proposed owning-boundary correction, **not implemented or approved yet**: one
authoritative corner-preserving route allocation feeding both solver geometry and
reference/pin correspondence. Solver preparation must not discard validated bends.
Keep authored controls, sample budget and collision tolerances. Insufficient budgets
in other scenes need explicit semantics; a generic algorithm replacement is not justified.

## Verification

Inspection through the shared CLI succeeds; document revision 208. Native route
reproduction and direct whole-segment checks establish the failure above.
Local evidence: `probe.log`, `traced-probe.log`, `fixture.json`, `handoff-check.json`.
Temporary C++ tracing was removed; the baseline native library was rebuilt.
No production correction or canonical package replacement was performed.
Official libigl winding-number/signed-distance and CGAL path documentation consulted
before investigation. Existing native route diagnostics and regressions are the first
tools to use; no algorithm replacement is selected.

## Next actions

1. Discuss the sampling ownership and insufficient-budget policy with the user.
   The user explicitly chose “Discuss the approach first”; wait for their decision.
2. Once agreed, fix the owning boundary; log any computation change and qualify source,
   native, background GUI and one canonical portable package before normal integration.

## Recovery inputs

Original: `E:/development/WIP_models/solver_fail1.anthroforge`.
Local copy/evidence: `build/solver-fail1/`. Normal `.venv` and native build environment.
Keep all validation background-only and preserve unrelated root `__init__.py`.
