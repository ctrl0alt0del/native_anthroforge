# Investigate Ctrl-snapped curve dragging

- Task branch: `codex/snap-drag-investigation`
- Integration branch: `main`
- Starting revision: `f2758767ce3ecef1dbb84181bdd358a55a7b78e0`
- Status: in progress
- Last updated: 2026-10-17 (Europe/Bucharest)
- Active writer: desktop investigation chat

## Outcome and acceptance

Reproduce the reported approximately doubled frame intervals during Ctrl-snapped
curve dragging, establish the cause with discriminating measurements/experiments,
and identify which evidence the first on-demand profiler must collect. The user
confirmed a minimal case: new project, imported cube, Body primitive, edit a curve
point and snap it. No production anatomical scene is required.

## Decisions and relevant files

Use the shipped interaction path and repeatable mouse input. Compare unsnapped and
snapped runs, identify instrumentation overhead and separate CPU work from elapsed
frame intervals. Do not infer cause from the existing surface_snap timer alone:
it covers picking but excludes normal lookup and downstream editing/publication.
Keep disposable diagnostic output in ignored build directories. User wants ordinary
release builds to record actionable profiles without rebuilding for each investigation.

## Current state

Inspected CurveEditor.qml, curve_interaction.py, task execution, existing metrics and
GUI acceptance fixtures. Researched Qt scene-graph timing and binding profiling.
Added tools/snap_drag_diagnostic.py: the user's cube/Body fixture, repeated normal/
snapped drags, raw input/frame callback timestamps, CPU/wall measurements and optional
call attribution. No production behavior changed. Initial stable 120-event ABBA run
had normal handler means 28.1/30.7 ms and snapped 33.8/32.2 ms; surface picking averaged
0.08 ms. This does not establish a consistent 2x snap-specific regression. Broad Qt
signal/UI refresh costs dominate call attribution; next isolate their consumers.

Rejected the first QTest.mouseMove timing approach: QtTest internally calls
processEvents, so its duration includes unrelated queued work. Several such runs
crashed in Qt Core/Quick3D. Replaced measured move delivery with QMouseEvent/sendEvent
without nested event processing; the complete ABBA experiment then passed. The
crash's root cause is not established. Old normal-profile/snap-profile outputs are
invalid for end-to-end conclusions. Current raw results are local-only under
build/snap-drag-investigation/delivery-baseline.json and delivery-profile.json.
GUI frame callbacks are GUI-received frameSwapped timestamps, not GPU presentation.

Confirmed a causal UI bottleneck: replacing only the hidden Activity ListView's
model with an empty model, while preserving controller notifications, scheduling,
geometry and snapping, approximately halves input-handler wall time. In a same-
process 16-trial balanced comparison (120 moves/trial, Body lifted to the cube's
top plane so normal/snapped motions can match), original snapped trials averaged
38.7–46.8 ms/handler; empty-list trials 20.8–23.1 ms. Normal drags also improve.
Controller.notify emits activityChanged and Activity.qml assigns a newly reversed
QVariantList on every update, even while its containing panel is hidden.
Central diagnostic spans attribute most drag cost to Controller.refresh/notify;
surface_hit including normal lookup takes around 0.11–0.12 ms per snapped move.
This establishes a major drag bottleneck, not the claimed consistent 2x difference
between snapping and ordinary dragging. External application load is substantial
(observed about 11 CPU-core equivalents on this 24-thread PC), so absolute frame
times are not idle-machine benchmarks. Paired controls preserve that distinction.

Added opt-in diagnostic spans and activity-model counterfactuals in tools only.
No application import, native rebuild, product version bump or shipped profiler.
Discarded cProfile mode: mixed Qt/Python callback attribution is not a qualified
thread-specific CPU profile. Direct wall spans are labeled as such. Final harness
records source/platform/options, raw input positions and timing, GUI frame callback
timestamps, job lifecycle snapshots, and verifies snapping/undo. Final repetitions
and the development gate are pending at this checkpoint.

## Verification

Architecture checks passed (2 tests); diagnostic Ruff cleanup passed. Actual GUI
capture inspected: selected Body curve editing against imported cube. Stable snap
trials hit the target for all 120 moves. Pending causal intervention and final gate.
Preserve the unrelated untracked root __init__.py.

## Next actions and blockers

1. Complete final paired recording, including identical-path and undo checks.
2. Capture optional spans/model-change counts and run tools/check.ps1.
3. Preserve compact quantitative evidence and profiler requirements; report limitations.

## Recovery inputs

The existing Windows setup and native build suffice. Use examples/primitives/cube.obj.
The containing commit identifies this checkpoint; inspect history for remote reachability.
