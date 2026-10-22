# VCP performance analysis for 0.2.4

Analysis date: 2026-10-22. Production baseline: `ae9eaab52f8ebc96488a53a57cbe06255bb8aca3`,
application 0.2.3, Python 3.12.12, Windows 11, 24 logical CPUs. This is an investigation
and proposed optimization scope, **not an implemented 0.2.4 release**. No production
code, numerical contracts, source projects or portable package were changed.

## Main finding

The expensive tissue mathematics already runs in C++. The clearest remaining costs
are repeated scene-wide work, Python metadata traversal, native preparation that is
discarded between calls, and one genuinely expensive native height-smoothing solve.
Moving all application orchestration into C++ would not address these causes by itself.

## Evidence and workload

The saved migrated assembly contains 59 SCPs, 96 tissues, 96 membranes, 326 Fibers and
11 ordinary curves. Of the tissues, 94 use Section Profile and two use Control Point;
all have stacking disabled, smoothing Off and relaxation None. Consequently additional
native and two-layer stacking fixtures were used to exercise the missing paths.

The original `skeleton_four_muscles_v001.anthroforge` was not modified. The assembly
input was the already-qualified save from the opening investigation:
`E:/development/WIP_models/muscle_reconstruction_workflow/runs/2026-10-21-standalone-all-muscle-transfer-958f7969/diagnostics/open-optimization-20261022/packaged-final/saved.anthroforge`.
Probes open a disposable copy. The single-tissue target is Rectus abdominis.L section1,
`0204fc95-39fc-4102-8fa6-94f0231ab007`, with 13,845 base vertices and 27,136 triangles.

Three serial recorder-off trials measure elapsed cost. Separate runtime recordings
attribute work; main-thread cProfile runs locate Python call amplification. cProfile
is not used to compare Python/native speeds: deterministic profiling biases that
comparison, as explained in the [Python documentation](https://docs.python.org/3.12/library/profile.html).
Native fixture calls were repeated three times; stacking comparisons five times.
The machine was not an isolated benchmark host; ranges are observations, not guarantees.

### Assembly edits, profiler off

| Operation | Synchronous command | Command through all jobs settled |
| --- | ---: | ---: |
| Increase one Section Profile's depths by 1% | 14–19 ms | 1,023–1,043 ms |
| Ten such edits before waiting | 119–124 ms total | 1,152–1,183 ms |
| Move one source Fiber's middle control point 1 mm | 128–176 ms | 1,846 ms cold; 1,156–1,215 ms warm |
| Translate Ribs SCP 1 mm | 117–166 ms | 4,539–4,617 ms |

The ten-edit workload consists of ten committed API commands, not one continuous UI
gesture. Coalescing already works: it produced one rest/intrinsic/plan/final chain.
No failed jobs occurred. Ribs movement genuinely affected a large hierarchy: 211
Fiber paths, 70 construction evaluations and 63 tissue phase chains. Those counts
alone do not establish unnecessary invalidation.

**All-jobs settled is not geometry latency.** In the recorded single-tissue edit,
inflation took 28 ms and the final tissue published about 128 ms after capture began.
Two subsequent/overlapping collision checks accounted for 849 ms of native wall
duration; the final check ended around 1.06 s. Worker durations overlap other work;
do not add inclusive categories or subtract profiler cost to invent a clean latency.

### Numerical coverage, recorder off

| Workload | Observed duration | Scope |
| --- | ---: | --- |
| Section Profile | 18–20 ms | 13,845-vertex single part |
| Control Point | 16–18 ms | Same base |
| Distributed | 42–46 ms | Same base; includes native direction diffusion |
| Normal shell inflation | 42–48 ms | Same base, 27,690 output vertices |
| Height smoothing | 1,560–1,661 ms | Same base, 552 fixed samples |
| Geometric relaxation | 30–35 ms | Normal shell |
| Static PBD, 24 iterations | 141–152 ms | Normal shell; usable ITERATION_LIMIT result |
| Radial construction, resolution 128 | 0.73–0.91 ms | 642 output vertices |
| Profile sweep | 39–44 ms | 1,024 path samples × 32 profile samples |

The PBD result is not claimed converged. Its diagnostic distinguishes iteration
limit from numerical failure. These are comparative fixtures, not complete geometry
parity certification or measurements of every branch/constraint/preset combination.

## Proposed optimization work

### A. Make advisory Fiber collision checking incremental

Observed: [fiber_collisions.py](../src/anthroforge/application/issues/fiber_collisions.py)
uses one document scope and invalidates it on broad result/pose changes. A change to
one tissue runs the full 326-path × 154-surface batch repeatedly. The native routine
is already batched C++; the problem is the work requested and repeated preparation.

Independent calls measured 441–457 ms for the complete batch and 152–154 ms for one
Fiber against the same 154 surfaces. The single-Fiber row exactly matched the full
result and used the same tolerance. This also shows that merely narrowing paths is
insufficient: capturing the unchanged surface world remains substantial.

[routing_world.cpp](../native/src/routing_world.cpp) recaptures colliders, closed-edge
counts and transformed bounds for each advisory call. Immutable leased routing scenes
and a bounded cache already exist in [routing_scene.py](../src/anthroforge/native/routing_scene.py),
but [path_collisions.cpp](../native/src/path_collisions.cpp) does not consume them.

Proposed ownership:

- Application Issues provider tracks changed path/surface-role revisions and retains
  evidence for unaffected pairs. Schedule coherent accepted inputs, not every intermediate stage.
- Native query layer reuses immutable collider preparation and a scene broad phase;
  expose an appropriate collision-scene lease through the existing ownership/cache infrastructure.
- Keep miss-to-hit detection, intentional contact intervals, missing surfaces, removals,
  pending provenance, cancellation and stale-result rejection. Preserve the global
  tolerance convention; simply querying smaller target subsets can change it.

Acceptance: compare every finding with exhaustive checking across tissue and bone
edits, removal, role changes and undo. Measure actual final-geometry latency and time
to current findings separately. The incremental implementation has not been built.

### B. Remove repeated Python metadata traversal

Observed: [accepted_result](../src/anthroforge/application/evaluation_results.py) scans
every object against every input port to find pending owners. The Ribs cProfile run
observed 12 million executions of that inner generator. This is metadata work, not
a numerical algorithm that needs porting.

A disposable alternative builds an owner set once, preserving document order and
all revision capture. For the assembly's 480 saved tissue-stage read sets (21,017
ports, maximum 87 per result), five full passes took **504–568 ms** with the existing
function versus **32–90 ms** with set membership; medians **540 and 32 ms**. Complete
returned EvaluationResult records were equal. This isolated test is not a claimed
whole-application 17× improvement and does not cover every pending-state combination.

Further measured call amplification: ten depth edits caused global point-identity
validation 20 times. The earlier opening work already skips structural validation for
evaluated-only changes; authored numerical edits still conservatively repeat it.
Extend the existing typed validation boundary to distinguish changed relationships,
point identities and topology from scalar parameters. Do not disable validation.

Acceptance: pending Manual prerequisites, authored versus accepted revisions, invalid
references, duplicate points, topology edits, cancellation and historical saves must
behave identically. Benchmark repeated real edits with the profiler off.

### C. Retain native stacking preparation and reduce boundary transfers

Observed: [tissue_stack_evaluation.py](../src/anthroforge/application/tissue_stack_evaluation.py)
constructs a fresh native StackSession for planning and again for final evaluation;
final evaluation repeats planning. The native engine already has reusable caches.
MaterialLease caching also already exists; adding a second material cache is not the proposal.

A two-membrane fixture, each with 625 output vertices/1,152 triangles, was evaluated
with fresh versus retained sessions. The disposable adapter change was confined to a
sequential diagnostic process; production code was not changed.

| Comparison | Fresh session | Retained session | Evidence |
| --- | ---: | ---: | --- |
| Unchanged plan, warm | median 17.6 ms | approximately 1.0 ms | Existing native cache reused |
| Unchanged final, warm | median 175.9 ms | approximately 5.0 ms | Exact vertex equality |
| Receiver inflation changed | median 174.1 ms | 156.8 ms | Exact vertices and triangles on five edits |
| Provider inflation changed | median 176.9 ms | 172.8 ms | Exact equality; no convincing speedup |

This is evidence for eliminating duplicate unchanged work, **not** a 35× claim for
interactive stacking edits. Changed providers still require expensive resolution.

[tissue_stack_scene.py](../src/anthroforge/application/tissue_stack_scene.py) also
exports each SCP's geometry through NumPy, creates transformed world vertices and
converts triangle indices, then native code copies them into collider snapshots.
`Mesh.array` itself is a zero-copy borrowed view; the transform, integer conversion
and subsequent native recapture are the transfers to target. Native planning also
exports full point arrays when the caller only needs orders/dependencies.

Proposed: bounded, exclusively leased native stacking contexts; retain qualified
preparation across compatible plan/final jobs; use native mesh handles plus frames
for obstacles; separate metadata-only planning from selected geometry retrieval.
Do not share one mutable solver across concurrent jobs. Preserve complete read sets,
provider-first order, selected regions, exact constraints, independent surface validation,
fallback semantics and resource release. Measure multi-provider changed-input cases
before estimating a production speedup.

### D. Optimize the native height-smoothing problem, not its language

Observed: height smoothing is already a C++ cotangent-biharmonic constrained QP using
PIQP. One report spent 1,529 of 1,582 ms inside the solve, with 24 iterations. Fixed
samples and displacement bounds were respected; measured stationarity was about
6.3e-10. Therefore caching the roughly 50 ms of preparation alone cannot solve this bottleneck.

[smoothing_core.cpp](../native/src/smoothing_core.cpp) constructs a new energy/session
each call. The pinned PIQP wrapper supports updates, but this caller loses that state.
[assembly.cpp](../native/migration/smoothing/src/assembly.cpp) represents fixed values
as equality rows and other per-variable bounds as identity inequality rows. The
vendored [PIQP API](../native/vendor/piqp/solver.hpp) supports native variable bounds.

The next discriminating native experiment should compare the current formulation
against fixed-variable elimination plus direct box bounds, preserving the exact
quadratic objective and independent KKT/constraint certification. Separately measure
symbolic reuse and compatible solver updates. Neither alternative was implemented
or timed here. Do not promise a faster solver, reduce tolerances, or replace smoothing
with a different visual result to obtain favorable numbers.

### E. Reuse native tissue geometry preparation

Observed in source: Section Profile rebuilds source frames and evaluates the same
longitudinal profile repeatedly across rows. Distributed inflation rebuilds mass and
cotangent matrices and a sparse factorization. Tissue stages can repeatedly build
full mesh acceleration/render buffers while passing intermediates between kernels.

These are native optimization opportunities, not Python loops. Candidate changes:
cache immutable material frames/operators by accepted geometry; evaluate longitudinal
profile coefficients once per column; reuse sparse symbolic analysis where the matrix
pattern is unchanged; retain canonical topology and prepare only the capabilities a
stage actually needs. Draft/final mesh APIs already exist, so extend their use rather
than creating another geometry representation.

Changing inflation distance changes the Distributed system's numerical coefficients:
reusing its numerical factorization blindly would be incorrect. Eigen explicitly
separates [pattern analysis from numeric factorization](https://libeigen.gitlab.io/eigen/docs-5.0/classEigen_1_1SimplicialLDLT.html).
Intermediates are inspectable and may be attachment providers; lazy preparation must
still satisfy those consumers. These sub-costs have not been individually timed,
so prioritize them after the measured repeated-work problems.

## Profiler limitations found by this investigation

The large Ribs recording took 7.50 s versus 4.54–4.62 s without recording. Its 1,230
resource-payload observations consumed 2.11 s inclusive, and resource-reference
limits were reached 360 times. The report correctly marks itself incomplete. Event
retention did not evict trace records; ownership attribution is the incomplete part.

The profiler recursively rediscovers payload references at preparation/execution
boundaries. Provide explicit owned-resource enumeration or reuse immutable snapshot
reference sets; keep observation bounded and recording-only. This should accompany
the early optimization work so follow-up measurements remain useful. It is not
production overhead when recording is off, and its timings cannot be exactly
subtracted from the recorded application durations.

The final recorded inventory estimates about 774 MB of unique owned payload, about
498 MB reachable from the current document. History and catalogue totals overlap
those allocations; they are not additive, and this does not establish a leak. Counts
exclude Python/Qt/driver overhead and inherit the recording's ownership limitation.

## Desktop evidence

Hidden viewport measurements and source review are being finalized. They must use
normal change-triggered refresh, not a benchmark that forces full refresh each frame.
Offscreen texture readback is not physical display latency, and a viewport-only test
does not qualify the complete inspector or a real pointer gesture.

## Reproduction and delivery limits

Local-only raw evidence and disposable scripts are in `build/vcp-performance-024/`:
`assembly_probe.py`, `kernel_probe.py`, `focused_probe.py`, `viewport_probe.py`, JSON
measurements, cProfile captures, runtime `.afprofile.zip` recordings and hidden images.
Source assets and large reports are intentionally not committed. This document keeps
the measured conclusions recoverable through Git.

No computation-history change entry is needed: this analysis changed no production
algorithm, cache or execution boundary. Implementing any recommendation must update
[the computation inventory/history](computation_history.md), qualify actual geometry
and attachment behavior, and pass the applicable development/desktop/package gates.
