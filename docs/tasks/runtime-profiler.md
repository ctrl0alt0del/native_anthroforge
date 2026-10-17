# Runtime profiler 0.1.4

- Task branch: `codex/runtime-profiler`
- Integration branch: `main`
- Starting revision: `7e6451e9c6760474b6d0c00c0e4f6746fcf238a4`
- Status: in progress
- Active writer: desktop implementation chat

## Outcome and acceptance

Implement the confirmed 0.1.4 runtime profiler: explicit start/reproduce/stop/share,
automatic QML attribution, shared input/command/task/native/publication boundaries,
120-second/128-MiB recent-history capture and a versioned JSON trace ZIP. Runtime
operations and headless collection must not change document or scheduler semantics.
Activity presentation remains unchanged; its deferred bottleneck is the acceptance
case recorded in [snap-drag investigation](snap-drag-investigation.md).

## Decisions

Qt 6.12.0 private profiling client is isolated in a native desktop adapter. Dormant
profiling support initializes before the QML engine; debugger/inspector services
remain excluded. Detailed Python/C++ stack sampling and report viewing are deferred.
The report distinguishes inclusive wall time, collector costs, unavailable CPU/GPU
attribution, clock uncertainty and dropped/truncated records. Recording is never an
authored operation, calculation, undo entry, or reason to block project saving.

## Current state and verification

Native Qt adapter and development startup qualification are implemented. Real UI
capture identifies Activity.qml:23 and records QML bindings/JavaScript/signals and
render-thread frame milestones. Native build/contracts, function-size tests and
new native-file style checks pass. Shutdown required explicitly destroying the
profiler client before its connection: the client owns other connection children.
The corrected development process exits successfully. Portable build is in progress.
The shared runtime service, bounded ring, atomic ZIP export/retry, runtime API,
F12 controls, model observer, native input dispatch and shared application boundaries
are now implemented. Nine new headless/buffer/lifecycle tests and mypy pass. Native
build passes; desktop smoke and screenshot inspection pass with clean shutdown.
This checkpoint is still not merge-ready. Preserve untracked __init__.py.

Development qualification: `python -m anthroforge.desktop.app --profile-probe
build/profiler-qualification/development.json` produced 1,748 binding events with
source locations, 144 frame milestones, zero adapter drops, and clean shutdown.
Portable qualification also passed with cleaned environment: 1,710 QML binding
events, Activity source locations, no drops, clean exit. Complete final packaging
must be repeated after the rest of the implementation.
`tools/profiler_qualification.py` prepares serial cube/body drag comparisons; it
ran a serial none/dormant/dormant/none/record comparison. Handler means (normal/snap)
were 28.43/33.82, 29.56/33.36, 29.75/33.10, 29.50/32.62 ms. The first recording had
adapter drops because its diagnostic drainer only transferred one chunk per tick;
production draining now handles bounded batches on its background worker. Final
complete-build comparison and clock/memory/error qualification remain outstanding.

Full recorder GUI acceptance passed the first two hidden-Activity normal/snapped
gestures: F12 start/stop preserved the drag and undo, files had zero drops. Snapped
report alone shows Activity.qml:23 binding mean 19.45 ms, Controller.notify 25.78 ms,
native pick 0.030 ms and normal query 0.016 ms. This is attribution evidence, not an
unprofiled performance estimate. The visible-panel harness initially began its drag
before panel layout settled; it is corrected to settle layout before projection.
Complete four-case rerun, robustness review, final gate and packaging still pending.

## Next actions

1. Implement/qualify the Qt adapter in development and the packaged executable.
2. Build bounded runtime collection, shared boundaries, controls and export.
3. Exercise lifecycle/error/ring/headless and actual GUI acceptance; compare disabled,
   dormant and recording costs, run the gate, package and integrate only when qualified.

## Recovery

Use normal Windows setup/build tools; Qt SDK and .venv live in ignored directories.
Production fixture is generated from examples/primitives/cube.obj plus a body curve.
Push coherent checkpoints under work_continuity.md; no additional agents are active.

2026-10-17 checkpoint: four GUI cases passed on the preceding recorder build, and
Perfetto v58.2 imported the trace (112,293 slices, no import errors). The development
gate passed 405 tests before subsequent robustness changes. New lifecycle tests cover
active/queued jobs, cancellation, collector failure and native hook restoration.
Current robustness changes add heap-ordered retention, bounded unfinished-span metadata,
fixed histogram storage, build identity, explicit Qt decoding costs and UI active-job
snapshots. Native build and 15 targeted tests pass. A tighter initial summary-name cap
hid Activity attribution in the GUI rerun; restored a 2,048-name budget with compact
histogram arrays. Final GUI rerun, overhead trials, full gate/package remain pending.

Final review added: bounded pending model-discovery events, incomplete Qt span endings,
semantic shortcut events, safe command target IDs, compact slowest-source summaries,
Qt-free subprocess coverage, timestamp-ordered late-batch eviction and pending-span
budget tests. Package checks now exercise full headless/desktop report export.

Serial full-recorder trials (120 normal + 120 snapped inputs each) found cold means
24.88/29.18 ms with support disabled, 25.75/29.09 dormant, 35.25/40.52 recording.
The first normal-drag dormant difference is retained as an unresolved first-use effect;
it is not erased by the warmed result. Eight counterbalanced trials after 60 warm-up
moves gave disabled 31.62/32.01 ms and dormant 31.30/32.38 ms, within run-to-run variation.
Forced disk caching did not establish a remedy and was not adopted. More Activity
history after warm-up changes absolute workload; compare only within each series.
Latest final metadata additions require refreshed recording/GUI evidence. Full gate,
packaged reports, short-window stress, trace import and final review remain pending.
