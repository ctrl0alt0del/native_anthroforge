# Investigate Ctrl-snapped curve dragging

- Task branch: `codex/snap-drag-investigation`
- Integration branch: `main`
- Production baseline: `f2758767ce3ecef1dbb84181bdd358a55a7b78e0` (0.1.3)
- Status: investigation delivered; specific snap-versus-normal ratio remains unconfirmed
- Last updated: 2026-10-17 (Europe/Bucharest)
- Active writer: desktop investigation chat

## Outcome

Found and causally isolated a substantial UI bottleneck in the user's minimal
fixture: new project, imported cube, Body primitive, edit and drag a curve point.
The hidden Activity ListView replaces its model on every activity notification.
Disconnecting only that view's model approximately halves input-handler time,
while calculations, snap queries, feedback and controller notifications continue.
This affects normal dragging too. **A consistent 2x snap-versus-normal regression
was not established.** Do not present this as a complete explanation of that ratio.

Only diagnostic tools and evidence changed. Application/native code, version and
packaged executable are unchanged. The runtime profiler and production Activity
fix remain implementation work; this task provides their evidence/acceptance case.

## Evidence

All values below are means per trial. Final experiments used 120 moves per trial.
Compact evidence from 24 trials is committed in
[snap-drag-evidence.json](snap-drag-evidence.json), including SHA-256 hashes of raw
local recordings. Original/empty/empty/original controls ran in one process.

| Measurement | Original Activity model | Only Activity model disconnected |
| --- | --- | --- |
| Snapped input handler, final control without call spans | 31.81 / 36.66 ms | 17.51 / 18.41 ms |
| GUI receipt interval of frameSwapped, same control | 57.76 / 67.08 ms | 35.79 / 39.23 ms |
| Controller.notify, separate span recording | 17.84 / 21.19 ms | 4.28 / 4.35 ms |
| Activity modelChanged count per 120 moves, span recording | 127 / 127 | 0 / 0 |

Complete `surface_hit`, including normal lookup, took 0.117–0.124 ms per call in
the span recording. The narrower existing `surface_snap` metric measured about
0.08–0.10 ms in the final control. `Authoring.refresh` still cost approximately
5.6–6.0 ms in the span recording; that separate cost has not been optimized.

The responsible path is `CurveEditor.updateDrag -> Controller.transformDelta ->
authoring_actions.transform_delta -> Controller.refresh -> Controller.notify ->
activityChanged -> Activity.ListView.model`.

Controller.notify rebuilds descriptions for the latest 40 jobs and emits the
activity signal. Activity.qml binds `workspace.jobs.slice().reverse()` to the
ListView model. Hiding its parent in Main.qml does not suspend that binding.
Inspection, measured replacements, call spans and removal/restoration of only the
view's model jointly establish the cost. Qt documents the reset behavior of list
values and incremental notifications available with item models:
[Qt model documentation](https://doc.qt.io/qt-6/qtquick-modelviewsdata-cppmodels.html).

An earlier balanced 16-trial comparison measured original normal handlers at
33.8–45.6 ms and original snapped handlers at 38.7–46.8 ms. Empty-list trials were
19.5–22.0 ms normal and 20.8–23.1 ms snapped. The large improvement follows the
Activity intervention, not simply Ctrl being held or released.

## Limits and rejected experiments

- Windows, Python 3.12.12, PySide 6.12.0, Ryzen 9 7900X3D (24 logical processors),
  RTX 4080. Another application used approximately 11 CPU-core equivalents at one
  observed sample. These are not idle-machine benchmarks. Balanced comparisons
  reduce drift but do not eliminate OS/GPU contention.
- Initial Body height was z=0. Later controls use z=0.5, the cube's top plane, so
  normal/snapped motion has comparable geometry. Recorded paths differ by at most
  0.002102 m in this fixture due to integer cursor/anchor rounding (subpixel).
  They are not numerically identical trajectories.
- Frame timestamps are GUI receipt times of frameSwapped, including delayed delivery
  while the UI is busy. They are **not GPU/compositor presentation timestamps**.
  No vsync explanation of the user's doubling was established.
- Timed movement uses QMouseEvent/sendEvent through the production gesture.
  QTest.mouseMove was rejected because it calls processEvents and mixes queued
  work into its duration. Several initial experiments crashed in Qt Core/Quick3D;
  their cause remains unproven. Subsequent qualified recordings completed with
  non-reentrant delivery. This is not an application-crash fix claim.
- Exploratory cProfile suggested expensive signal emission but gave unsuitable
  mixed Qt/Python thread attribution. The final tool removes that mode. Optional
  spans measure nested inclusive wall time with Python thread identity, not CPU
  samples. Never sum inclusive spans as disjoint costs.
- Freezing all activity notifications was a broad initial intervention. Emptying
  only the ListView model isolated the consumer. Neither counterfactual is a
  production fix that preserves the activity display.
- Hiding snap feedback did not establish a cause: separate runs drifted even for
  their unsnapped controls. Do not claim a benefit from removing the overlay.
- final-paired.json and final-spans.json briefly overlapped and are excluded from
  quantitative evidence. They supplied coordinate/undo checks only. The later
  qualified-control.json and qualified-spans.json ran serially with no concurrent
  AnthroForge benchmark/build; these are the primary final measurements.
- Controls without call spans still have the input driver, frame timestamp callback
  and existing app metrics. Spans are not a zero-cost observer. Under changing load,
  differences between separate runs cannot quantify exact profiler overhead.

## Evidence-derived requirements for the first profiler

| Evidence that helped | Required saved data |
| --- | --- |
| Tiny query versus long drag handler | Whole input-to-publication timeline, beyond geometry timers |
| Expensive synchronous signal consumers | Python/native attribution and QML binding/model activity, including hidden views |
| 127 model replacements for 120 moves | Event counts, durations and input correlations |
| Running/obsolete jobs and result adoption | Enqueue/dispatch/cancel/finish/adopt events, job/target IDs and revisions |
| Delayed GUI callbacks | Distinct GUI/render/submission/presentation tracks; label unavailable data |
| Normal/Ctrl phases and machine load | Interaction mode, held actions, scene size, update/display settings and environment |
| Inclusive wall time versus CPU | Separate wall time, CPU time and sampling estimates |
| Recording perturbs execution | Collector work, buffers/bytes, dropped events and limitations |

Use an on-demand recording service with bounded buffers and structured events at
shared input, command, coordinator and publication boundaries. Automatic stack and
binding collectors should discover expensive feature work without bespoke markers
in every feature. Disabled recording must leave collector threads, sampling timers,
trace buffers and per-event allocations inactive. Preserve existing scheduler
measurements that affect functional scheduling decisions.

Export a versioned JSON summary plus detailed timeline/stack tables in one bundle.
Include build/symbol identity, collector options, clocks, threads, missing attribution
and lost events. Put collector work in a separate category and measure enabled
cost with controlled A/B runs; cache/scheduling disturbance cannot be exactly
subtracted from every event.

Collector choice remains unqualified for the packaged Nuitka executable. Development
Python support alone is insufficient. Current native Release settings do not request
matching debug symbols; stale PDB files are not proof of usable symbol coverage.
This investigation has not implemented a runtime profiler or guaranteed universal
marker-free attribution.

First acceptance case: in an ordinary release build, start recording, drag normally,
hold/release Ctrl, stop and share the file. From that file alone, identify the slow
UI path and model churn, separate query and total handler time, and state which
render/presentation evidence exists. No investigation-specific rebuild or feature
markers. Then qualify the Activity fix using the same recorder, including the
open Activity panel.

## Owning boundary for a later production fix

Activity presentation should expose a stable incremental model keyed by job identity,
update changed roles/rows and keep cheap status summaries independent of hidden
row rendering. QAbstractListModel is already used by RenderModel in this repository.
Preserve scheduling, jobs, cancellation, undo and checkpoint semantics. Verify both
open and closed panels. Suppressing notifications would hide required information.
This design follows the evidence but is not yet a validated production fix.

## Reproduction and outage recovery

Run serially from the Windows checkout with the existing native/Qt setup:

```powershell
uv run --no-sync python tools/snap_drag_diagnostic.py --mode snap --events 120 --repeats 1 --intervention paired-activity --output build/snap-drag-investigation/control.json
uv run --no-sync python tools/snap_drag_diagnostic.py --mode snap --events 120 --repeats 1 --intervention paired-activity --spans --output build/snap-drag-investigation/spans.json
```

Omit `--mode snap` for normal/snapped ABBA comparisons. JSON and per-trial captures
live in ignored build directories. Each trial checkpoints; the final complete flag
is written only after gesture/undo checks succeed. Writes use atomic replacement.
Raw captures remain local; compact evidence, code and this handoff are committed.

## Verification and next work

- Final recordings: every snapped move hit the target; undo restored the initial
  point; no QML warnings. Actual GUI captures inspected, including snap feedback.
- tools/check.ps1 passed: lint/format, types, native build/style, script style,
  396 pytest tests, native numerical checks and doctor.
- Final serialization smoke passed: completed gesture/undo recording has complete=true
  and atomic replacement leaves no temporary file.
- Ownership review: production layers unchanged; diagnostics and counterfactuals
  are confined to tools. No production sampler, per-feature marker or scheduler
  alteration. No numerical geometry calculation moved into Python.
- No portable rebuild for these diagnostic-only changes. Packaged profiler support
  and actual presentation latency remain unverified.
- Preserve unrelated untracked root __init__.py.

Next product work: implement and qualify the recording service against this case,
then optimize activity presentation using recorded evidence. The exact reported
snap-specific doubling still needs an in-app recording if it persists.
