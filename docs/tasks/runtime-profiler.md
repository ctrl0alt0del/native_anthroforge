# Runtime profiler 0.1.4

- Task branch: `codex/runtime-profiler`
- Integration branch: `main`
- Starting revision: `7e6451e9c6760474b6d0c00c0e4f6746fcf238a4`
- Status: final validation; implementation complete, integration pending
- Active writer: desktop implementation chat

## Delivered behavior

Explicit F12/Record → reproduce → Stop → one `.afprofile.zip`, with automatic Qt
binding/source attribution, native input/render/model collectors, shared command/task/
native-call boundaries, bounded 120-second/128-MiB capture and atomic background export.
Desktop and Qt-free headless clients use profile.start/status/stop. Export failure keeps
the frozen capture for retry. New/Open preserve the application recorder and subsequent
native/task observation. Recording does not change undo, scheduling or save checkpoints.

Qt 6.12.0 private APIs are isolated in native/profiling; debugger and inspector services
are excluded. Detailed stack sampling, GPU profiling and report viewing are deferred.
The Activity production fix remains deferred, as recorded in
[snap-drag investigation](snap-drag-investigation.md).

## Evidence and remaining work

[Qualification evidence](runtime-profiler-evidence.json) stores compact measurements
and trace hashes. [Development status](../development_status.md#runtime-profiler-014)
explains validation and measurement limits; [profiling](../profiling.md) documents the
workflow, report schema, ownership budget and overhead interpretation.

Completed: prior full gate (413 tests), repeated five-case GUI drag/undo/cancel/focus
acceptance, current GUI New/Open lifecycle checks, headless lifecycle tests, bounded
retention stress, Perfetto import, and relocated minimal-PATH desktop/headless portable
checks. The final New/Open ownership fix has targeted tests and GUI acceptance; the
full gate and portable rebuild are running again before integration.

Overhead comparisons ran serially and counterbalanced, with system utilization recorded.
Warmed idle differences stayed within observed run variation; small cold/first-use
variations remain uncertain. Recording has a measurable observer effect. No exact
subtraction or zero-overhead claim is made. Two focus-interrupted benchmarks are excluded.

Next: finish gate, commit/push the lifecycle fix, rebuild/requalify the portable executable,
refresh evidence and source archive, then merge/push normally to main. Preserve the
unrelated untracked root __init__.py. No additional agents are active.

## Maintenance lessons

- Destroy the Qt profiler client before its connection; the client owns connection children.
- Start with periodic flush disabled; reset it only after recording completion is acknowledged.
- Probe mode uses app.exit, matching smoke mode, because app.quit can encounter the normal
  unsaved-document close prompt. Production close/save semantics remain unchanged.
- A native render callback must never enter Python. GUI timestamps describe submission,
  not physical display latency. Overlapping inclusive spans are not additive.
- Session replacement must not replace the desktop recording service. Scheduler construction
  reconnects profiling through one shared initialization path; borrowed engines detach on close.

## Recovery

Use the ordinary Windows setup/build tools; Qt SDK, environment, captures and binaries
are ignored local artifacts. Generate the fixture from examples/primitives/cube.obj and
a body curve. Continue the existing branch, inspect remote/checkpoint state and use normal
checkpoint pushes under work_continuity.md. No force pushes or Git history replacement.
