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
The shared runtime service, controls, report/export and lifecycle integration remain
unimplemented; this checkpoint is not merge-ready. Preserve untracked __init__.py.

Development qualification: `python -m anthroforge.desktop.app --profile-probe
build/profiler-qualification/development.json` produced 1,748 binding events with
source locations, 144 frame milestones, zero adapter drops, and clean shutdown.
This proves collector functionality, not overhead or the complete acceptance case.
`tools/profiler_qualification.py` prepares serial cube/body drag comparisons; it
must run without competing builds/benchmarks before interpreting measurements.

## Next actions

1. Implement/qualify the Qt adapter in development and the packaged executable.
2. Build bounded runtime collection, shared boundaries, controls and export.
3. Exercise lifecycle/error/ring/headless and actual GUI acceptance; compare disabled,
   dormant and recording costs, run the gate, package and integrate only when qualified.

## Recovery

Use normal Windows setup/build tools; Qt SDK and .venv live in ignored directories.
Production fixture is generated from examples/primitives/cube.obj plus a body curve.
Push coherent checkpoints under work_continuity.md; no additional agents are active.
