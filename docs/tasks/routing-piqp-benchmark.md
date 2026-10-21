# Routing QP backend comparison

- Branch: `codex/routing-piqp-benchmark`; integration: `main`.
- Baseline: `c5a163f`; status: investigation and benchmark implementation.
- Writer: current desktop chat, direct work. Background/headless only.

## Request and boundaries

Compare the current routing inner solver with PIQP for performance. Keep the route
planner, quadratic model, pin/contact equations, trust limiting, collision checks and
outer acceptance algorithm unchanged. Do not switch the shipped backend or overwrite
user projects. Numerical assembly, solving and repeated subproblem trials stay in C++.

## Approach

Use an isolated benchmark library reusing the qualified native object files, replacing
only the routing-solve translation unit with a generated, guarded experimental adapter.
The original migrated header and normal build remain untouched. Verify baseline output
equivalence before timing. Compare paired identical subproblems and serial counterbalanced
complete cold/warm routes. Include compact production fixtures, the actual solver_fail1
failure, curve/fiber ownership and workload scaling. Report setup/assembly/solve time,
residuals, route validity, failure rates, variability and profiling overhead separately.

PIQP already ships in the repository for smoothing/stacking. Its official interface
supports sparse/dense quadratic programs and updates only with fixed dimensions/pattern:
https://predict-epfl.github.io/piqp/interfaces/python/getting_started
https://predict-epfl.github.io/piqp/

## Recovery and remaining work

1. Implement and qualify the isolated native comparison adapter and runner.
2. Run matched subproblem and full-route trials; inspect geometry and profiler evidence.
3. Record reproducible results, limitations and recommendation; run relevant development
   checks and merge benchmark tooling/docs only. No production algorithm change is implied.

Local builds/reports belong under ignored `build/routing-piqp/`. Preserve the unrelated
root `__init__.py` and all source `.anthroforge` files.
