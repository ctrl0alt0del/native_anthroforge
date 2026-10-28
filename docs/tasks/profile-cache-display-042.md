# Profile recommendations R09–R11

- Task branch: `codex/profile-cache-display-042`
- Integration branch: `main`
- Starting revision: `05fb548`
- Status: complete
- Last updated: 2026-10-28, Europe/Bucharest
- Active writer: local Codex

## Outcome and acceptance

Profile aggregate cache retention, duplicate in-flight preparation and viewport
publication on the existing assembly. Distinguish observed costs from possible
optimizations; this request does not change production algorithms or release versions.
Keep project inputs unchanged and all desktop validation hidden/offscreen.

## Decisions and relevant files

- Scope: R09–R11 in [the audit](../recommendations_042_audit.md).
- Reuse runtime profiler, resource ownership and existing shortcut workload tooling.
- Qt's partial `QQuick3DGeometry` setters do not guarantee partial GPU uploads:
  <https://doc.qt.io/qt-6/qquick3dgeometry.html>.
- Initial hypotheses: aggregate cache growth, simultaneous duplicate preparation and
  expensive buffer replacement. The measured distinctions are recorded below.

## Current state

Profiling is complete. Only experiment tools, their evidence-classification tests and
documentation changed. Production algorithms, cache policies, geometry, attachment
behavior, package versions and source projects are unchanged.

### R09: cache retention and rebuilding

The assembly contains 58 SCPs and 96 tissues. Six cycles alternate Ribs Top Radius,
Humerus Length, Radius Length and Thumb thickness between the prior test values and
their original values: 24 committed edits, followed by undo/redo and a cache clear.
The source is opened read-only through project adoption, not overwritten.

| Settled state | Estimated native resources | History-owned resources | Cache-exclusive resources | Process private memory |
| --- | ---: | ---: | ---: | ---: |
| Before edits | 627.3 MiB | 559.1 MiB | 68.3 MiB | 1,660.8 MiB |
| After 24 edits | 2,339.3 MiB | 2,268.0 MiB | 71.3 MiB | 3,779.4 MiB |
| After clearing caches | 2,268.0 MiB | 2,268.0 MiB | 0 MiB | 3,804.3 MiB |

History overlaps the document and other owners; these columns must not be added.
Private-memory readings include Python, allocator retention and recorder storage, and
are not immediate live-allocation totals. The native inventory excludes opaque fiber
preparations; their separate cache charges remain bounded near 64 MiB. Both native
bytes and cache charges contain estimates. This is a 24-edit session, not an hours-long
leak certification. Reopening the source in the completed lifecycle trial returns history
to 559.1 MiB. The dominant growth in this case belongs to undo history, not aggregate
cache retention. Do not silently prune history as a cache optimization.

There is real completed-cache churn: 2,547 fiber preparation misses, 75 hits and 2,495
byte-budget evictions. Only 211 distinct keys were involved; 2,336 misses revisit an
evicted key. All native fiber preparation calls total **1.846 s inclusive** across the
74.155 s edit sequence. This is an overlapping subphase cost, not a guaranteed possible
wall-time reduction. Tissue preparation had 804 distinct misses and 740 entry-limit
evictions, with no evicted-key rebuild in these edits.

An experiment-only 1,024 MiB fiber allowance retained all 211 preparations (380.17 MiB
of charged storage), reducing misses to 211 and giving 2,411 hits with no evictions.
This is not a recommended new default: timings varied too much to establish a small
end-to-end gain. Current fiber byte charges include shared parent meshes and retained
attachment fields, so summing entry charges overstates exclusively allocated storage.
First distinguish preparation-owned bytes from shared resources, then design aggregate
budgeting/eviction using rebuild cost. Do not simply increase every independent limit.

The full-body skin reference has 154 anatomical sources. A separate FAST experiment
uses 128 handles and changes constraint strength 100 → 110 → 120 → 100 → 100:

| Preparation | Time | Cache behavior |
| --- | ---: | --- |
| First strength 100 | 131.243 s | Disk miss; creates weights |
| Strength 110 | 21.053 s | Disk hit; second native preparation |
| Strength 120 | 21.384 s | Disk hit; evicts first preparation at the two-entry limit |
| Return to 100 | 21.126 s | Disk hit; rebuild after eviction |
| Repeat 100 | 0.136 ms | In-memory hit |

Each native preparation reports **552.30 MiB**; two retain **1,104.60 MiB**. The newly
created disk entry is **18.92 MiB**. This supports cost-aware memory and disk retention,
not a universal small cap that would repeatedly discard expensive skin preparations.
The disk trial used an isolated copy under `build/`; the user's cache was not modified.
Existing native BBW convergence warnings occurred on the cold solve; cache reuse is
not convergence certification. Identity results, predictions and diagnostics have the
same SHA-256 before eviction, after rebuild and on a memory hit.

### R10: identical in-flight work

Across 3,358 preparation/cache misses in the default 24-edit sequence there were **zero
overlapping identical keys from different jobs/threads**. Cache events identify the key,
job and thread; the analyzer distinguishes a later miss after eviction from a concurrent
miss before insertion. No event eviction occurred in these edit captures. Separate tissue
consumers mostly use distinct accepted base handles; repeated fiber keys occur serially.

The lookup/build/store race remains possible in the implementation. This workload does
not demonstrate a material benefit from single-flight ownership/cancellation machinery.
Defer R10 until a representative workload actually exhibits expensive overlapping keys;
fixing completed-cache retention is a separate mechanism.

### R11: display updates

Ribs Top Radius → 3 was repeated in a hidden 1280×960 D3D11 viewport. All anatomy and
construction remain loaded. Calculation and staged presentation run together, with a
60 Hz pacing target. Image readback happens only after timing. This is CPU submission
and application-loop evidence, not GPU execution or physical display latency.

Three runtime-recording-off trials took **28.95, 29.27 and 42.87 s**; boundary-recorded
trials took **36.18, 35.67 and 45.39 s**. Headless Ribs updates ranged about **5.5–8.6 s**
across the session. Rendering adds fiber display jobs and scene publication, so these
are different workloads, not a pure rendering speed ratio. Background utilization and
process CPU time are recorded; variance precludes a precise profiler-overhead estimate.

In the 29.27 s unrecorded trial:

- Update ticks consumed 19.455 s; presentation callbacks consumed 6.669 s.
- CPU render submission consumed 1.269 s; sync consumed 0.118 s; end-frame 0.396 s.
- Construction synchronization consumed 5.633 s within update work.
- Picking input reconstruction consumed 2.064 s and resource collection 1.669 s within
  presentation work. These nested inclusive figures must not be added to their parents.
- Measured loop work had a 69.2 ms median and 112.8 ms p95. Idle frames were much cheaper.

The scoped counters find **306 scene refreshes**, **396 geometry activations**, and
**132,498 construction record visits for 549 changed records**: 99.59% of visits leave
the row unchanged. `ConstructionProjection.update_record` computes world transforms and
ownership before checking its cache. Every activation rebuilds whole-scene surface
snapping/picking matrices and runs resource collection. These are demonstrated costs.

The final trace observes about **55.63 MiB** of staged surface/fiber chunk payloads;
main surface delegates also maintain a separate outline geometry. This is logical CPU
payload, not a measured GPU transfer count. An isolated native Qt adapter probe copied
44.03 MiB across 250 first-chunk asset setters in **3.24 ms median** (five trials; first
7.72 ms). Detached geometry excludes GPU upload and display. Combined with the frame
breakdown, this does not justify prioritizing buffer-copy work over repeated scene work.
Qt explicitly does not guarantee partial GPU updates from its partial-data setter.

Recommended first experiment: target construction projection by changed dependencies;
retain unchanged transform/ownership projections; publish/pick each displayed revision
coherently with reused unchanged inputs; avoid repeated full reachability scans within
the same publication. Preserve delayed/staged picking correctness and resource leases.
Only reconsider indexed GPU topology reuse or navigation detail after measuring the
remaining render cost. No such optimization has been applied here.

## Verification

Style/format checks and 19 focused tests pass, including architecture/function lengths,
profiler diagnostics, resource ownership and experiment event classification. Initial
native test invocation used the stale `build/dev` DLL and failed on a missing export;
the complete selected set passes with the qualified DLL below. No production rebuild
or release qualification was needed or claimed.

Desktop/headless Ribs outputs have identical fingerprints for 1,210 geometry arrays,
resolved poses, attachment metadata and canonical oriented connectivity. Captures were
visually inspected. The larger-cache probe preserves bindings and canonical topology;
direct numerical comparison finds maximum coordinate drift **4.09e-14 m**. Thumb's raw
triangle enumeration differs, with unchanged oriented connectivity, as in prior Boolean
qualification. Cache clearing itself preserves geometry exactly.

The ordinary profiler hits its 4,096-handle inventory cap during the long session and
does not enumerate fiber preparation payloads. The experiment uses separate, settled,
expanded inventories up to 65,536 mesh/path handles, with complete ownership accounting
for their supported kinds. This does not change the recorder's production budget.
Both gaps should be corrected before an aggregate budget relies on profiler totals.

The first full-Qt trial lost initial events to ring eviction and timed out stopping while
the harness blocked GUI event processing. It is excluded from complete evidence. The
first boundary trial also evicted early events. Final boundary captures 2/3 use a bounded
512 MiB experiment recorder, have zero evictions/losses and finish normally. Full Qt
profiling is not necessary to establish the measured application-boundary costs above.
The cold skin trial exceeded its original 120-second trace interval; its complete wall
duration comes from the independent outer timer. The maintained tool now uses 360 seconds.

The first expanded harness failed only at a final nonexistent `new` operation; the
completed tooling uses real source-project adoption and all final lifecycle runs pass.

## Next actions and blockers

1. Profiling and review are complete; no production optimization was included.
2. Proposed implementation priority: R11 scene/publication work, R09 accounting and
   cost-aware budgeting; defer R10 without a demonstrated workload.
3. History growth is a separate policy/design discussion, not implicit approval to
   discard undo states. No algorithm or runtime-policy change is authorized by profiling.

## Recovery inputs

- Production input: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
- Native build: `C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native`;
  set `ANTHROFORGE_NATIVE_LIBRARY` to its `bin/af_native.dll`.
- Keep outputs under ignored `build/cache-display-profile`; preserve root `__init__.py`.
- Local evidence: `expanded/` (24-edit default retention), `budget-probe/` (larger-cache
  discrimination), `compare-64/` and `compare-1024/` (numerical arrays), `skin/` (isolated
  FAST cache), `display-boundary-2/3.afprofile.zip`, corresponding JSON and PNG captures.
- Reproduce with `uv run --no-sync python tools/profile_cache_retention.py OUTPUT 6 64`,
  `tools/summarize_cache_profile.py OUTPUT`, and `tools/profile_display_publication.py
  OUTPUT_PREFIX [--unrecorded]`. Desktop also requires `AF_NATIVE_BUILD` set to the
  qualified build directory. The source tree and ignored native build must agree.
- Skin: `tools/profile_skin_cache_retention.py OUTPUT
  build/skin-041/assembly-reference/retained.anthroforge`. Raw reports/arrays/source assets
  stay local; tools, numerical conclusions and task context are committed for recovery.
