# Viewport responsiveness and worker ownership

- Task branch: `codex/viewport-worker-responsiveness`
- Integration branch: `main`
- Starting revision: `60b64ec4`
- Status: implementation in progress
- Last updated: 2026-11-27, Europe/Bucharest
- Active writer: desktop chat, primary agent only

## Outcome and acceptance

Implement the confirmed camera invalidation, scene projection, cached skin readiness,
owned worker input, bounded UI completion and CPU admission proposals. Audit synchronous
work that can safely execute off the UI thread and verify actual multicore use. Preserve
camera persistence, geometry/diagnostic invalidation, Draft/Final semantics, undo, save,
atomic publication and rejection of obsolete results.

## Evidence and decisions

The preceding audit reproduced one mirroring check per camera save: `workspaces` is
incorrectly treated as a mirroring input. Scene projection compares the entire workspace;
skin panel context computes readiness before its unchanged-state guard. On synthetic
256-cube scenes, maximum UI ticks were 162 ms, and 112 ms with only mirror invalidation
suppressed. These are Qt event-loop measurements, not rendered-frame measurements.

The coordinator already has two worker threads. Capture, admission, publication and UI
projection run on its owning thread; four bounded interactive policies allow inline work.
Use the existing coordinator and status owner rather than adding competing worker queues.

## Current state

Implemented camera field deltas, mirror input invalidation and pose-aware source validation,
camera-only projection consumption, camera-independent scene caches and shared cached skin
readiness. Camera-only edits retain persistence and do not invoke the skin planner.
Inspection resource validation/source preparation and captured skin read-revision assembly
have moved to owned worker inputs. Desktop result publication has a shared 2 ms admission
window; each result remains atomic and contexts rotate to avoid starvation.

CPU audit: ordinary attachment/routing/tissue native translation units are serial per job;
skin fields and fitting are separate OpenMP targets with up to four threads. The default
coordinator's two workers therefore do not imply two-core execution for every operation.
CPU scheduling changes and rendered/packaged acceptance are still pending.

## Verification so far

- Focused camera/mirror/status/projection tests: 25 passed.
- Issue lifecycle/integration and tissue inspection tests: 21 passed.
- Ruff and mypy passed before the later worker/publication changes; rerun required.
- Same local 256-cube Qt event-loop probe: camera-triggered jobs 7 to 0; maximum camera
  tick 162.29 to 2.22 ms, p95 93.14 to 0.78 ms. No rendered-frame claim. Raw baseline is
  in the prior probe directory; candidate is `build/viewport-responsiveness/probe-results.json`.
- Skin update/topology/automatic-pipeline and painting checks are running at checkpoint time.
- Full gate, CPU scaling, production scene, GUI and packaging checks have not yet run.

## Next actions

1. Add regression cases and implement semantic camera/domain invalidation and status caching.
2. Audit and reduce synchronous capture/publication; verify native CPU policies and ownership.
3. Measure baseline/candidate, run development gate and actual viewport/packaged acceptance.
4. Update architecture/computation history, checkpoint, reconcile and integrate after validation.

## Recovery inputs

Use the shared environment `E:/development/anthroforge/.venv` with explicit PYTHONPATH to
this checkout. Existing native library: `build/skin-pipeline/bin/af_native.dll`; Qt SDK:
`E:/development/anthroforge/.tools/qt/6.12.0/msvc2022_64`. External AVBD checkout at
`E:/development/anthroforge/build/application-boundaries` is read-only and independently dirty.
The root checkout has unrelated assembly work; leave it untouched. Prior local-only probe:
`C:/Users/alexe/.codex/visualizations/2026/11/25/01a21362-f926-7710-8635-1f759dbc0849/job-thread-audit/`.
