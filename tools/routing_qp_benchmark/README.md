# Routing QP comparison lab

This Windows-only experiment substitutes the routing **inner quadratic subproblem**
solver. It does not change the production DLL, migrated kernels, public API, package
or accepted routing safety policy. PIQP 0.6.4 is the existing pinned dependency.

The quadratic objective is `0.5*x'P*x + q'x`, with the existing banded Hessian and
negative RHS. Pin equations become `A*x=b`; linearized contact rows become
`G*x >= G*current - linear_gap`. Trust limiting, exact pin restoration, collision
sweeps, acceptance, corridor planning and output validation remain the original code.
Sparse PIQP reuses setup only when all sparsity patterns agree; dense PIQP reuses
setup when dimensions agree. Assembly, pattern checks, setup/update and solve are
all included in candidate and complete-route timings. There is no solver fallback.

## Reproduce

Build the normal native target first (`tools/build-native.ps1`), then:

```powershell
tools/routing_qp_benchmark/build.ps1
uv run --no-sync python -m tools.routing_qp_benchmark.pilot
uv run --no-sync python -m tools.routing_qp_benchmark.run --audit --rounds 12 --output build/routing-piqp/results.json
uv run --no-sync python -m tools.routing_qp_benchmark.summarize build/routing-piqp/results.json build/routing-piqp/summary.json
```

The lab links the exact current production source-list object files, avoiding stale
objects left by removed source files. Only `routing_solve.cpp` is replaced. Its source
and kernel includes are generated under ignored `build/`; the pinned SQP donor hash
and each insertion point are checked. Rebuild the normal target after changing any
production source. `pilot` requires bit-identical current-backend samples, parameters
and counters before comparing alternatives.

`run --backends 0,1 --tolerance 1e-6` supports sensitivity trials. Backend 0 is the
current implementation, 1 sparse PIQP, 2 dense PIQP. Primary trials use `1e-9` for
PIQP absolute/relative residual and gap tolerances; the outer solver tolerances are
unchanged. Twelve serial rounds rotate all six backend orders. Cold routes discard
the native obstacle-scene cache; warm routes receive the same accepted current-backend
path and a prepared scene. Warm trials do not simulate a new authored edit.
Use `--rounds 0 --audit --audit-input warm` for a separate matched warm-QP capture.

`--skull` includes four existing captured anatomical fibers from the local-only
`build/skull-routing-inputs.json`, with its hash recorded in the report. The full
capture is intentionally not committed. `qualification` uses that capture for a
30-round production-DLL versus lab-backend-0 comparison and separate `.afprofile.zip`
captures. `visuals` uses optional Matplotlib to render route overlays without windows.
These two commands require the local skull capture. They are not portable acceptance
tests and are not run by the regular development gate.
`counterexample` tests the historical skull pin against the existing native outward
snap in an in-memory copy. It does not rewrite fixtures or original project files.

## Interpret evidence

The complete-route trials disable per-QP timers, matrix diagnostics and CSV collection.
They include the normal Python native-call packing and native scene/planner/solver/
validation work. Mesh import, GUI, task scheduling and presentation are outside this
boundary. The separate runtime-profiler captures observe the registered native calls;
their durations are not substituted for the unprofiled timings.

Paired diagnostics run all three backends twice on each identical current-route SQP
state, in rotated forward/reverse order. A seventh solve continues the current route.
Diagnostic totals are not complete-route performance measurements. Reported residuals
are on the quadratic candidate **before trust limiting**, not final route penetration.
When the existing bounded active set returns unequal active/dual lengths, stationarity
is unavailable; the adapter does not guess missing multipliers or patch the production
algorithm. Native whole-segment clearance checks and exact authored pins validate the
final paths separately.
Unqualified native outputs remain in reports with `quality.clear=false` and a count of
invalid results. A successful native return alone does not make a trial valid. Current
backend component timing columns are unmeasured; only its total candidate time is used.

System CPU load, timings and variance are retained. Thermal state, OS core placement
and other processes are uncontrolled; these are local workload measurements, not a
universal ranking or an application FPS claim. Results and interpretation belong in
`docs/tasks/routing-piqp-benchmark.md` and the computation history.

References: [PIQP](https://predict-epfl.github.io/piqp/),
[C++ integration](https://predict-epfl.github.io/piqp/interfaces/c_cpp/installation),
[update contracts](https://predict-epfl.github.io/piqp/interfaces/python/getting_started).
