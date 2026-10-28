# Implement measured R11 display updates, then R09 cache budgeting

- Task branch: `codex/display-cache-042`
- Integration branch: `main`
- Starting revision: `b7c5d99`
- Status: complete
- Last updated: 2026-10-28, Europe/Bucharest
- Active writer: local Codex

## Outcome and acceptance

Implement the measured display/scene-publication improvements first, then shared cache
ownership, aggregate cost-aware retention and bounded FAST disk storage. Follow
[engineering guidelines](../engineering_guidelines.md) and the
[profiling evidence](profile-cache-display-042.md). Keep geometry algorithms, attachments,
undo history, scheduling contracts and staged display/picking correctness intact.

## Decisions and relevant files

- R11 belongs to incremental presentation projections, displayed picking inputs and
  resource reachability. GPU topology changes lack evidence and are not this increment.
- R09 belongs to engine-owned cache/resource accounting and FAST cache persistence.
  Do not trim document/history owners or add in-flight work sharing (R10).
- Qt recommends batched model updates and avoiding redundant binding work:
  <https://doc.qt.io/qt-6/qtquick-performance.html>.
- Retain 0.4.2; deliver its single canonical portable package after qualification.

## Current state

Both increments are implemented and checkpointed. R11 targets construction/tissue projection,
reuses frames, coalesces publication and caches retained-document reachability. R09 deduplicates
cache allocations, coordinates aggregate retention and bounds persistent FAST products.
Production profiling, numerical comparisons and regression qualification are complete.
The canonical 0.4.2 package is rebuilt and passes all 32
relocated checks. Root `__init__.py` remains untouched.

## Verification

Focused regression, paired profiling, hidden rendering, native tests/style, type/lint checks
and portable checks pass. The final serial suite passes **2,641 tests** in 351.78 s;
all six native suites, native/Python style, formatting, typing, numerical imports and the
native-runtime doctor pass. The initial full suite had an external tetrahedral-process access
violation and a collected older assertion from the new frame-coalescing test. The external
case and corrected test pass both in isolation and in the complete serial rerun.
No numerical algorithm, production retry or exception suppression was added for that crash.
An intervening direct `pytest` launcher could not import repository `tools`; using the
project's `python -m pytest` entry point resolved collection without code changes.
The relocated executable passes 32 checks with a minimal PATH. Hidden native GPU images
show the expected tissue and mirror geometry; ordinary offscreen UI captures establish
layout only. No physical interactive desktop acceptance is claimed.

## Delivery

No remaining implementation or qualification work. The canonical executable is
`dist/0.4.2/AnthroForge.dist/AnthroForge.exe`, with companion
`dist/AnthroForge-0.4.2-source.zip`. The packaged runtime is revision `890ed85`;
subsequent changes update qualification documentation only. The source archive includes
the new implementation/tests and dependency headers, excludes root `__init__.py`, and
passes ZIP integrity checks. Normal integration preserves the checkpoint history.

## Recovery inputs

Use `ANTHROFORGE_NATIVE_LIBRARY=C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native/bin/af_native.dll`
and `AF_NATIVE_BUILD` pointing to that build directory. The default `build/dev` DLL is
stale. Production fixtures and baseline profiles are documented in the profiling task.
Keep new artifacts under ignored `build/display-cache-042`; preserve root `__init__.py`.

## R09 checkpoint

Shared allocation receipts, a 4 GiB aggregate estimated-payload budget with cost-aware aggregate eviction, fiber/skin retention and bounded FAST disk products are implemented. Existing numerical kernels unchanged. Focused cache/native/profile tests pass; expanded production captures report complete inventories without loss. Eight-edit numerical comparison: bindings/canonical topology equal, maximum coordinate delta 4.09e-14 m. Do not compare two-cycle and six-cycle final coordinates directly: the baseline itself has history-dependent repeated-edit differences; matched sequences are required.

At this checkpoint full qualification was pending; subsequent results follow below.
Artifacts are under `build/display-cache-042`. The detached baseline worktree uses `b7c5d99`
plus only the shared profiling harness runtime-path correction and the pre-change native DLL.

## Production evidence

Serial BAAB hidden D3D11 trials (same 58-SCP/96-tissue project, Ribs Top Radius to 3):

| Measure | Before | After |
| --- | ---: | ---: |
| Complete update, two trials | 29.763 / 29.182 s | 22.666 / 24.125 s |
| Median complete update | 29.472 s | 23.395 s |
| Construction record visits | 132,498 | 549 |
| Construction synchronization, median inclusive | 5.682 s | 3.121 s |
| Picking input preparation, median inclusive | 1.972 s | 0.582 s |
| Resource collection, median inclusive | 1.705 s | 0.389 s |

This is a 20.6% shorter median update (1.26x throughput), not a frame-rate or GPU-latency
claim. Background/system load was recorded and is uncontrolled. Runtime recording was off;
identical experiment boundary timers remain. All four final geometry/pose/attachment and
canonical-connectivity fingerprints match exactly. A separate first after-trial was 24.167 s.
Screenshots were inspected; no visible desktop interaction was used.

The 24-edit recorded run has no calculation errors and no report losses. Fiber preparation:
211 misses, 2,411 hits, zero evictions versus 2,547 misses/75 hits/2,495 byte evictions before.
Deduplicated fiber retained payload: 105.42 MiB. The complete cache union is about 201 MiB;
history still retains 2,268 MiB after 24 edits. Private process memory is about 3,793 MiB;
this is not a claimed memory reduction. Expanded recorder coverage now includes the previously
missing fiber preparation payload. Cache clearing preserves the document fingerprint exactly;
undo/redo and reopening complete without errors. Matched eight-edit arrays differ at most
4.09e-14 m, with exact retained bindings and canonical oriented connectivity. Raw Thumb triangle
enumeration has the pre-existing Boolean ordering difference.

Whole-body FAST, 128 handles, strengths 100/110/120/100/100: 113.827 s cold, 19.022/18.452 s
for the new strengths using disk weights, then 0.087/0.113 ms from retained preparations.
Previously returning to strength 100 rebuilt for 21.126 s because of the two-entry cap.
Three preparations retain 1,656.90 MiB within the aggregate limit. Identity output, diagnostics
and predictions have the same SHA-256 as the baseline. Cold BBW iteration-limit warnings are
unchanged; this does not establish stronger convergence. The isolated disk contains eight
products totaling 22.69 MiB and does not modify the user's cache.

Raw evidence: paired-summary.json, numerical-parity.json, display-before/after JSON/PNG,
cache-after and cache-parity traces/arrays, and skin traces under build/display-cache-042.

The final ordinary runtime-profiler capture takes 27.191 s and exports 59,565 events,
with no losses and an identical final geometry/attachment fingerprint. Recording overhead
is not subtracted from application time. CPU render submission does not measure GPU time
or physical display latency. The offscreen evidence does not establish interactive acceptance.

## Ownership and coupling review

- Projection invalidation belongs to the desktop change-journal consumer; geometry evaluation
  and scheduler ordering remain unchanged. Ordinary transform dependencies are distinct from
  anatomical attachment relationships. Inspection offsets remain separate picking frames.
- Session reachability caches only immutable document reference sets. It still sweeps newly
  orphaned resources and drops cached sets when document/history/checkpoint/job owners disappear.
- Cache coordination belongs to the native-resource boundary, under one short admission lock.
  Numerical construction stays outside that lock. Receipts retain identity/size metadata;
  document/history/job/view leases control lifetime independently of eviction.
- Aggregate eviction uses a cost/size/aging policy; specialized local caps retain their LRU
  behavior. Cost is a lookup-to-admission wall estimate, not an exact CPU construction measure.
- Disk writers use an OS lock; failed/contended persistence never blocks a valid solve.
  Owned interrupted staging files are cleaned only while no writer can be active. Other
  temporary files are preserved. No in-flight work-sharing framework was introduced.
