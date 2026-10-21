# Routing: current quadratic solver versus PIQP

- Branch: `codex/routing-piqp-benchmark`; integration: `main`.
- Production baseline: `c5a163f`; experimental adapter checkpoint: `ae0d1e9`.
- Date: 2026-10-21. Direct work, background/headless only.
- Status: complete; measurements, full gate and clean reproduction passed. Benchmark-only delivery.
- Scope: comparison experiment. **Production routing and the packaged app are unchanged.**

## Result and recommendation

Sparse PIQP is useful for heavier contact problems in this test set. It is slower on
small problems and most cold anatomical routes. Dense PIQP is consistently slower,
becoming prohibitively expensive at the larger tested sizes. Keep the existing default;
the evidence justifies investigating an adaptive sparse-QP choice. A safe selection
policy has not been established by this experiment.

Complete-route median milliseconds, including preparation/setup and unchanged planning,
collision and acceptance work (12 serial, counterbalanced trials per cell):

| Fixture / starting state | Current | PIQP sparse | PIQP dense |
| --- | ---: | ---: | ---: |
| Actual solver_fail1, 24 samples, attached pins, cold | 12.04 | 15.98 | 19.07 |
| Snapped cube, 32 samples, attached pins, cold | 8.85 | 13.43 | 34.82 |
| Snapped cube, 64 samples, attached pins, cold | 13.62 | 20.42 | 138.55 |
| Snapped cube, 64 samples, attached pins, warm | 52.25 | 41.31 | 195.27 |
| Snapped cube, 128 samples, attached pins, warm | 78.45 | 41.38 | 1,049.39 |
| Snapped cube, 256 samples, attached pins, cold | 91.83 | 53.27 | 6,477.28 |
| Snapped cube, 256 samples, attached pins, warm | 379.37 | 72.76 | 9,617.37 |
| Anatomical skull fiber 2, 64 samples, cold | 45.43 | 48.86 | 109.60 |
| Anatomical skull fiber 2, 64 samples, warm | 12.63 | 15.05 | 52.89 |

The heavy warm case improves **5.21x** with sparse PIQP; its cold case improves 1.72x.
Warm means every backend receives the same accepted current-backend path and a cached
obstacle scene. It is not a simulated point drag. Both ordinary-curve and anatomically
bound fiber inputs were tested. These are route timings, not UI, attachment-job, frame
or whole-application timings.

All 22 cases and distributions are in the machine-readable
[evidence](routing-piqp-evidence.json). Raw files, traces and inspected route overlays
are under ignored `build/routing-piqp/`. Reproduction commands and ownership are in the
[lab README](../../tools/routing_qp_benchmark/README.md).

## Controlled substitution

An isolated DLL reuses production object files and replaces only the routing-solve
translation unit. A hash-guarded generated header adapts the quadratic candidate
boundary. Application and migrated kernel sources remain untouched. The lab's current
backend reproduces production samples, parameters and counters exactly on all 22 inputs.

The same Hessian, RHS, pin equations and linearized contact inequalities are assembled
in C++. PIQP 0.6.4 sparse/dense use the existing pinned library. Setup is reused when
dimensions/pattern permit. Matrix construction, setup/update, result copy and solve are
included in cost. No Python optimizer, per-iteration callbacks or extra worker pool is
introduced. Trust limiting, exact pin restoration, CCD, acceptance, planning and final
validation are unchanged. PIQP failures do not silently fall back to the current solver.

Primary PIQP residual/gap tolerances are `1e-9`, maximum 250 iterations. A separate
22-case comparison at `1e-6` preserves the conclusion: the heavy warm fiber takes
68.05 ms versus 400.38 ms current; the actual 24-sample failure fixture remains slower
with PIQP. Outer safety tolerances are unchanged. This is a sensitivity experiment,
not a proposed production tolerance change.

## Why workload matters

Current routing exploits the banded path system and solves active contacts through a
dense Schur system. It is cheap with few contacts. Sparse PIQP pays more setup and
interior-point work on small systems but handles larger contact systems better here.

A separate paired experiment runs each identical current-route quadratic problem
through every backend twice, in rotated forward/reverse order; only the current result
advances the route. On the 256-sample warm fiber, with up to 259 contacts, summed
candidate cost is **373.82 ms current, 53.78 ms sparse, 10,751.10 ms dense**. These are
diagnostic timings, separate from the complete-route table. The gain is therefore not
solely a different outer iteration count. The complete warm sparse route also takes
40 trials versus 47 current trials.

Current candidates in that matched sequence reach a maximum linear-constraint violation
of 0.009832 before trust limiting, versus about `4.4e-16` for PIQP. This is **not final
route penetration**: all final snapped-cube routes pass independent segment checks
and retain exact authored points. The current active-set loop can exhaust its bounded
changes and return active/dual lists of unequal lengths; 34 of 94 matched invocations
show this mismatch. Stationarity is explicitly unavailable for these rows. This source-
level result-consistency risk is recorded for separate correction; no production repair
is part of the experiment.

Sparse PIQP's mean assembly, setup/update and solve costs in this warm sequence are
approximately 0.043, 0.240 and 0.857 ms per candidate. Current subcomponents are not
separately measured; only its total is compared. Cross-evaluation persistent PIQP caches
and alternate KKT backends were not tested. Point count alone cannot select a backend:
contact count and subdivision into pinned spans also matter.

## Correctness and the historical pin counterexample

The primary dataset has 1,584 complete-route trials: 22 inputs x 2 states x 3 backends
x 12 repeats. There are no native route-call failures. Independent clearance, finite
output, parameter ordering and exact pin checks pass **21 of 22 original input cases**
for every backend. Paired QPs report successful solves. Actual route overlays were
inspected against cube, user-project and skull geometry; numerical return codes alone
are not treated as geometry acceptance.

All backends flag the same first segment against the Cranium for `skull-AF_FIBER_1`,
despite native validated status. Its historical first pin is `5.50e-8` scene units
inside that surface; the advisory tolerance is `4.11e-9`. Fixed pins cannot move during
solving, and the routing owner-contact allowance differs from the advisory checker.
Projecting that pin through the existing outward-snap operation in a diagnostic copy
makes **all three backends pass**. This discriminates an input/contact-policy issue
from a PIQP benefit. The original capture and user projects are unchanged. The original
case is excluded from successful-clearance evidence, with its diagnostic recorded in
the JSON and `tools/routing_qp_benchmark/counterexample.py`.

## Measurement controls and limits

- Windows, AMD Ryzen 9 7900X3D (12 cores / 24 logical CPUs), clang-cl C++17,
  `/O2 /Ob2 /fp:precise`, Eigen parallelism disabled.
- Twelve serial rounds cover six backend orders twice; cold/warm order alternates.
  No build/test suite ran concurrently with timings. System CPU busy fraction was
  approximately 9–24%; other processes, core placement and thermal state are uncontrolled.
  Representative wall-time CVs are 8–17%. Small anatomical differences are not strong wins.
- Timed routes disable per-QP timers/diagnostics. Paired diagnostic candidate timing
  excludes subsequent residual calculation. Missing current component timings are not
  zero-cost claims.
- Thirty production-versus-lab-current rounds reproduce identical geometry, with median
  differences approximately -1.6% to +5.4%. Zero observer cost is not claimed; this is
  much smaller than the heavy sparse improvement.
- Separate existing profiler captures contain 28 native route calls per backend plus
  scene/cache work: `current.afprofile.zip`, `piqp-sparse.afprofile.zip`,
  `piqp-dense.afprofile.zip`. These are not the primary timing dataset.
- No interactive, packaged or cancellation qualification of a production PIQP backend
  is claimed. The shipped executable and source archive are not replaced.

## Validation and delivery

Experimental DLL builds with warnings as errors; native function-size check passes.
Python lint, formatting and function-limit checks pass. Full development gate passes:
1,442 Python tests, all three native tests, mypy, native/script style and native doctor.
The maintained lab build script was rerun after the gate's production rebuild; all 22
baseline identity comparisons pass again. The exact timed DLL is retained locally as
`build/routing-piqp/measured-af_routing_lab.dll`, matching the evidence SHA-256.
Ownership review: the lab stays outside application
imports, retains owned native inputs/results, and cannot select PIQP in the normal app.
Preserve the unrelated root `__init__.py` and all source projects.

Official references: [PIQP formulation and updates](https://predict-epfl.github.io/piqp/interfaces/python/getting_started),
[C++ integration](https://predict-epfl.github.io/piqp/interfaces/c_cpp/installation).
