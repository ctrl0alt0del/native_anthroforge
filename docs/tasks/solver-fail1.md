# Routed conversion failure in solver_fail1

- Task branch: `codex/solver-fail1`
- Integration branch: `main`
- Starting revision: `9cc6c7cd64ae3a0090bf3f715f434378653d441f`
- Status: correction implemented; release qualification in progress
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

User decision: sampling settings may adjust automatically. The authored sample setting
is now a preferred total; native preparation can exceed it to preserve required bends
and authored knots. It does not rewrite the authored setting, clearance or iteration cap.
The existing one-million-point native safety bound remains enforced.

Implemented one corner-preserving cold route allocation feeding solver geometry and
reference/pin correspondence. Removed the subsequent uniform resampling. Existing
valid warm-remap behavior is retained, with one cold replan when continuation fails.
Low-budget continuation tests exposed a second defect: zero-threshold clearance accepted
zero-distance segment crossings. Handoff checks now use the established positive
segment-check tolerance and include contained endpoints after contact-interval clipping.
The full clearance check remains separate from warm centerline feasibility.

## Verification

Inspection through the shared CLI succeeds; document revision 208. Native route
reproduction and direct whole-segment checks establish the failure above.
Local evidence: `probe.log`, `traced-probe.log`, `fixture.json`, `handoff-check.json`.
Temporary C++ tracing was removed. Corrected native build and three CTests pass.
41 targeted routing/layout tests pass, including existing addon/skull numerical parity,
warm continuation, growth from preferred counts 3/4, exact pins, closed loops and the
unchanged rejection of the captured faulty baseline seed.
Two application regressions plus architecture checks pass: direct conversion,
undo/redo, adaptive result persistence, consumer connectivity and attachment locks.
`tools/adaptive_routing_acceptance.py` passes against the supplied project: the original
24-point request solves, direct engine selection/undo/redo work, and requesting four
samples produces 13 accepted points with all authored points unchanged and clear segments.
Saved local corrected project: `build/solver-fail1/corrected.anthroforge`.
No canonical package replacement has been performed yet.
Official libigl winding-number/signed-distance and CGAL path documentation consulted
before investigation. Existing native route diagnostics and regressions are the first
tools to use; no algorithm replacement is selected.

## Next actions

1. Run the complete development gate and original-project GUI/shape qualification.
2. Qualify one canonical portable package; record final evidence and computation history.
3. Normal validated merge/push, preserving original file and unrelated changes.

## Recovery inputs

Original: `E:/development/WIP_models/solver_fail1.anthroforge`.
Local copy/evidence: `build/solver-fail1/`. Normal `.venv` and native build environment.
Keep all validation background-only and preserve unrelated root `__init__.py`.
