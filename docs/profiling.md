# Runtime performance recording

Press **Shift+F12** (also while holding Ctrl/Alt or dragging) to start recording.
Reproduce the slowdown and press Shift+F12 again. The **Record/Stop** button and View menu
provide the same action. Recording does not end an edit, change the document or add
an undo entry. **Show file** opens the report folder after background export finishes.
New and Open preserve the recording; document identifiers distinguish commands from
different documents within the same capture.

In 0.2.1, routing reports separate `af_routing_scene_capture` from `af_route_path_in_scene`.
The `routing_scene` cache records hits/misses/evictions/bypasses, and resource snapshots
include observed native capture capacities under `by_kind.routing_scenes`. Cache ownership
and job ownership overlap; do not sum them. The cache has a 64 MiB budget and eight-entry
limit; key/container overhead is conservatively budgeted, not an exact allocator measure.
Scene membership invalidation appears as `routing_scene_membership_changed`.

Reports are saved under `%LOCALAPPDATA%/AnthroForge/Profiles` on Windows. Share the
single `.afprofile.zip`. There is no report viewer in this release. An unsuccessful
export keeps the frozen capture; **Retry save** retries it. The runtime API can retry
with another destination. Only one capture/export is active at a time.

The default ring retains up to 120 seconds within a 128 MiB owned-storage budget.
The desktop reserves 64 MiB for adapter storage, bounded metadata, observers and export work;
64 MiB holds immutable application/Qt events. Older events are overwritten when
either retention bound is reached. Qt also owns transient producer buffers; these
are periodically flushed and are not a hard cap on total application RSS. Reports
state their actual retained interval and losses. Recording is off until requested.

`complete` describes collector completeness within the retained window. Intentional
ring eviction is counted separately; it does not mean the full recording was retained.
Events outside start/stop are filtered, and crossing spans are clipped and marked.

## Shared runtime API

These operations work through the usual Session/JSON authoring API, independently of
document commands. Headless operation does not load Qt. Available collectors are
listed in the report, so headless reports do not imply viewport coverage.

```json
[
  {"operation":"profile.start","arguments":{"seconds":120,"memory_mib":128}},
  {"operation":"primitive.create","arguments":{"kind":"BODY"}},
  {"operation":"wait","arguments":{}},
  {"operation":"profile.stop","arguments":{"path":"body.afprofile.zip","wait":true}}
]
```

`profile.status` returns state, recording ID, output path, errors, current storage
and collector information. States are idle, recording, stopping, exporting, saved
and export_failed. `profile.stop` with `wait:true` is for headless callers; the desktop
uses asynchronous completion to keep Qt processing events. Starting another capture
before the current one is saved/retried is rejected. Settings accept 1–3600 seconds
and 16–1024 MiB headless, or 96–1024 MiB with the Qt collector.

Invoke runtime operations on the owning session thread, like other application
operations. Worker threads can contribute spans; they do not control recording state.

## Reading a report

- `manifest.json`: schema version 1, application/build identity, platform, CPU,
  collector capabilities, viewport/Qt information, clock uncertainty, retention,
  completion/loss counts and measured profiler costs.
- `summary.json`: counts and bounded duration histograms, input distributions by
  event type/modifier mask, frame-submission intervals and attribution limitations.
- `trace.json`: Chrome Trace Event JSON with complete wall spans and timestamped
  lifecycle/model/frame events. Extract it to open in Perfetto or query with its
  trace processor. No application installation is needed to read these JSON files.

Durations and trace timestamps use microseconds. Source binding locations, native
function names, job IDs, authored/input revisions, execution modes and workload
counts provide context. Job events identify work already active at capture start
and still active at stop. Models report replacements/resets/row changes generically.
No mesh payloads, typed text or project contents are copied into the report.

Inclusive timings overlap: a command can include native calls and UI notifications;
a binding can include JavaScript. Do not add their totals. The percentile fields
are upper bounds from logarithmic histograms (1/16-octave buckets). Truncated spans
remain in the timeline but are excluded from duration distributions. Python spans
also include executing-thread CPU time where collected; wall time is not CPU time.
The export field `process_cpu_ns` measures the whole process during export and may
include concurrent application work. It is not isolated exporter-thread CPU cost.
`thread_cpu_ns` measures CPU used by the exporting thread itself.
Synthetic Qt trace lanes are described in `manifest.clock`; the QML lane represents
GUI-thread work, not an additional independent CPU thread.

Frame milestones are captured directly on the render thread. Submission does not
mean the monitor displayed a frame. OS input-queue wait, physical input latency,
GPU execution and detailed Python/C++ stacks are unavailable in v1. Unknown work
must remain unattributed rather than guessed.

## Recalculation, cache and memory evidence (0.1.8)

`summary.diagnostics` groups invalidation reasons, cache events and geometry-memory
samples. The detailed trace connects command parent spans, before/after revisions,
changed field names, invalidated output ports, jobs and replacement-job IDs. Reasons
distinguish changed inputs, newer requests, removed history versions and explicit
cancellation. Field values and geometry payloads are excluded. Bounded examples state
when details are truncated; use revision/ID relationships rather than assuming temporal
adjacency proves causation. A requested invalidation is not necessarily executed work.

The native Body base cache reports hit/miss, insert/reuse, oversized bypass, eviction
by byte budget or entry capacity, and lifecycle clear. Keys are opaque hashes. This
does not claim hit/miss coverage for every UI projection or dependency index.

`geometry_memory.latest` and `peak_observed_bytes` describe native mesh allocations,
including topology, vertices, prepared render buffers and estimated AABB-node storage.
Owners include document, history, checkpoint, active jobs, in-progress edit, asset
catalogue, base cache, displayed viewport and staged viewport. Alias handles sharing
one native allocation are counted once in `unique_bytes`. Owner totals overlap and
must not be added. `unattributed_bytes` exposes allocations without a known owner.
The trace also supplies Chrome `C` counter events named `geometry_bytes`.

Snapshots occur on existing coordinator ticks at most once per second and at recording
boundaries. Transient peaks and pre-recording job payloads can be missed. Inventory is
bounded to 4096 native handles, 256 observed jobs and 4096 weak job references; document
walks are bounded too. Truncation and observer failure are explicit losses, not zero
usage. Weak observations do not keep meshes alive. This is **not process RSS**: Python,
allocator overhead, Qt copies and GPU/driver allocations are excluded. AABB bytes are
an estimate based on the native tree's full-binary structure, not an allocator reading.
Inventory covers live handles in the observed native libraries; retained handles from
another session can legitimately appear as unattributed rather than current-document use.

No new memory queries or cache-event collection occur while recording is off. Measured
inventory and reference-observation cost appears under `manifest.profiler.resource_observation`
and profiler spans. Inclusive costs overlap and cannot be subtracted exactly. Existing
timing, completeness and retained-window interpretation still applies. The additive
report fields retain schema version 1; trace readers must accept counter events.

## Overhead and ownership

Task events also include `queue`: the destination workspace priority, local interactive
execution hint, causal request urgency/age, and last computed effective demand with its
donating job ID. Demand includes original queue age for replacement/FIFO analysis.
These timestamps use monotonic seconds, unlike trace event microseconds. A null demand
means the job has not needed queue ranking (for example immediate inline work).
`scheduler / prioritize` measures policy calculation separately. Temporary prerequisite
inheritance changes admission order; it does not preempt workers or bypass readiness.
See the [Ribs/Ulna comparison](tasks/task-priority-propagation.md) for the distinction
between required dependency waiting, runnable queue delay and viewport-model adoption.

The recording service is independent of documents, save checkpoints and scheduling.
Shared boundaries cover commands/transactions, task lifecycle, C ABI calls, UI
refresh/notification and publication. Qt automatically supplies bindings and source
locations. Future features using these boundaries require no bespoke markers.

Off means no event collection, recorder polling thread, capture buffers or report
writes. Qt profiling support is initialized dormant before the engine so recording
can start without restart. Its idle cost needs controlled comparison. Existing
scheduler timing remains active because it is functional application behavior.

While recording, the report measures buffer serialization, transfer/decoding, Qt
client decoding CPU/wall time and export work. Some scopes overlap; these are not
an exact removable tax. Qt producer hooks and cache/scheduling interference require
disabled/dormant/recording comparisons. Profiler UI work is identifiable separately.

The Qt adapter uses Qt 6.12.0 private client APIs behind an isolated native boundary,
with a local socket and profiling-only services. Qt upgrades require qualification.
Debugger/inspector services are excluded. API availability or development execution
alone does not establish packaged behavior.

Qualification tools: `tools/profiler_acceptance.py` exercises Shift+F12 during real drags;
`tools/profiler_qualification.py` compares disabled/dormant/recording modes serially.
Do not run builds or other benchmarks concurrently. `--disable-profiling-support`
is a desktop diagnostic baseline, not the normal launch mode. The explicit
`--profile-probe <file>` argument checks packaged Qt collector availability.

The [Activity investigation](tasks/snap-drag-investigation.md) was the first diagnostic
case. The [0.1.5 optimization](tasks/activity-panel-015.md) replaces repeated list
rebuilding with stable incremental rows. Its before/after reports retain the same
profiler schema and expose Qt row notifications without Activity-specific markers.
Profiler qualification and its limits are retained in [0.1.4 evidence](development_status.md#runtime-profiler-014);
current Activity comparisons are in [0.1.5 evidence](development_status.md#activity-presentation-015).


Official integration references: [Qt profiling service selection](https://doc.qt.io/qt-6/qqmldebuggingenabler.html),
[Qt Quick render signals](https://doc.qt.io/qt-6/qquickwindow.html),
[Perfetto external trace formats](https://perfetto.dev/docs/getting-started/other-formats).
