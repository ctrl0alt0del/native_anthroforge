# Runtime performance recording (0.1.4)

Press **F12** (also while holding Ctrl/Shift/Alt or dragging) to start recording.
Reproduce the slowdown and press F12 again. The **Record/Stop** button and View menu
provide the same action. Recording does not end an edit, change the document or add
an undo entry. **Show file** opens the report folder after background export finishes.

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

Frame milestones are captured directly on the render thread. Submission does not
mean the monitor displayed a frame. OS input-queue wait, physical input latency,
GPU execution and detailed Python/C++ stacks are unavailable in v1. Unknown work
must remain unattributed rather than guessed.

## Overhead and ownership

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

Qualification tools: `tools/profiler_acceptance.py` exercises F12 during real drags;
`tools/profiler_qualification.py` compares disabled/dormant/recording modes serially.
Do not run builds or other benchmarks concurrently. `--disable-profiling-support`
is a desktop diagnostic baseline, not the normal launch mode. The explicit
`--profile-probe <file>` argument checks packaged Qt collector availability.

The [Activity investigation](tasks/snap-drag-investigation.md) remains the first
diagnostic case. Profiling does not include its deferred production optimization.


Official integration references: [Qt profiling service selection](https://doc.qt.io/qt-6/qqmldebuggingenabler.html),
[Qt Quick render signals](https://doc.qt.io/qt-6/qquickwindow.html),
[Perfetto external trace formats](https://perfetto.dev/docs/getting-started/other-formats).
