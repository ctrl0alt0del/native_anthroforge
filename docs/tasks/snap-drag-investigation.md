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

## Verification

Architecture checks passed (2 tests); diagnostic Ruff cleanup passed. Actual GUI
capture inspected: selected Body curve editing against imported cube. Stable snap
trials hit the target for all 120 moves. Pending causal intervention and final gate.
Preserve the unrelated untracked root __init__.py.

## Next actions and blockers

1. Build a repeatable cube/Body dragging diagnostic and collect uninstrumented comparisons.
2. Attribute extra work and test a discriminating intervention.
3. Record verified cause, uncertainty and profiler requirements derived from the evidence.

## Recovery inputs

The existing Windows setup and native build suffice. Use examples/primitives/cube.obj.
The containing commit identifies this checkpoint; inspect history for remote reachability.
