# Implement measured R11 display updates, then R09 cache budgeting

- Task branch: `codex/display-cache-042`
- Integration branch: `main`
- Starting revision: `b7c5d99`
- Status: in progress
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

R11 implemented: journal-targeted construction/tissue projection, shared frame resolution, displayed-transform reuse, coherent frame publication, and immutable-document reachability caching. Focused regression and architecture checks pass (22 tests); lint and mypy pass. First hidden production capture: 24.167 s, 549 construction visits versus baseline 132,498; exact geometry/pose/attachment fingerprint equality. Full paired timing, delivery checks and R09 remain pending.

## Verification

Pending focused regression, paired production profiling, development gate, hidden GUI
and portable checks. No visible desktop interaction.

## Next actions and blockers

1. Implement and qualify incremental construction projection, picking and reachability.
2. Implement native resource receipts, aggregate retention and FAST disk budgeting.
3. Compare measured workloads, exact/canonical geometry and attachment fingerprints.
4. Run delivery checks, update evidence and package, merge and push.

## Recovery inputs

Use `ANTHROFORGE_NATIVE_LIBRARY=C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native/bin/af_native.dll`
and `AF_NATIVE_BUILD` pointing to that build directory. The default `build/dev` DLL is
stale. Production fixtures and baseline profiles are documented in the profiling task.
Keep new artifacts under ignored `build/display-cache-042`; preserve root `__init__.py`.

## R09 checkpoint

Shared allocation receipts, a 4 GiB aggregate estimated-payload budget with cost-aware aggregate eviction, fiber/skin retention and bounded FAST disk products are implemented. Existing numerical kernels unchanged. Focused cache/native/profile tests pass; expanded production captures report complete inventories without loss. Eight-edit numerical comparison: bindings/canonical topology equal, maximum coordinate delta 4.09e-14 m. Do not compare two-cycle and six-cycle final coordinates directly: the baseline itself has history-dependent repeated-edit differences; matched sequences are required.

Pending: full gate, repeated desktop timings (running serial BAAB), whole-body skin reuse, package and ownership review. Artifacts are under build/display-cache-042. Baseline detached worktree at build/display-cache-042/baseline uses b7c5d99 plus only the shared profiling harness runtime-path correction and the existing canonical pre-change native DLL.

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
