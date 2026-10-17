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
No reproduction or cause established yet. No production behavior changed.

## Verification

Pending controlled reproduction, call attribution and causal intervention.
Preserve the unrelated untracked root __init__.py.

## Next actions and blockers

1. Build a repeatable cube/Body dragging diagnostic and collect uninstrumented comparisons.
2. Attribute extra work and test a discriminating intervention.
3. Record verified cause, uncertainty and profiler requirements derived from the evidence.

## Recovery inputs

The existing Windows setup and native build suffice. Use examples/primitives/cube.obj.
The containing commit identifies this checkpoint; inspect history for remote reachability.
