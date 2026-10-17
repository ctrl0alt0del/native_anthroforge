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

Baseline inspected: clean tracked main, matching origin/main. Preserve unrelated
untracked root __init__.py. Implementation has not started and is not merge-ready.
Qt SDK includes QmlDebugPrivate client headers/library and packaged qmltooling plugins.
Runtime and portable qualification still required; header availability is not proof.

## Next actions

1. Implement/qualify the Qt adapter in development and the packaged executable.
2. Build bounded runtime collection, shared boundaries, controls and export.
3. Exercise lifecycle/error/ring/headless and actual GUI acceptance; compare disabled,
   dormant and recording costs, run the gate, package and integrate only when qualified.

## Recovery

Use normal Windows setup/build tools; Qt SDK and .venv live in ignored directories.
Production fixture is generated from examples/primitives/cube.obj plus a body curve.
Push coherent checkpoints under work_continuity.md; no additional agents are active.
