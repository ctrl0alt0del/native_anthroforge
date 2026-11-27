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
The default pool now admits up to four jobs, bounded by CPU count minus one logical CPU
of headroom. Native-team and memory demands remain shared across editing contexts. Final
deformation now reserves its four-thread quality kernel. This is admission headroom, not
OS affinity or a hard limit on external numerical processes.

## Verification so far

- Focused camera/mirror/status/projection tests: 25 passed.
- Issue lifecycle/integration and tissue inspection tests: 21 passed.
- Ruff and mypy passed before the later worker/publication changes; rerun required.
- Same local 256-cube Qt event-loop probe: camera-triggered jobs 7 to 0; maximum camera
  tick 162.29 to 2.22 ms, p95 93.14 to 0.78 ms. No rendered-frame claim. Raw baseline is
  in the prior probe directory; candidate is `build/viewport-responsiveness/probe-results.json`.
- Skin update/topology/automatic-pipeline and painting checks: 21 passed.
- Ownership, publication budget/fairness/shutdown, CPU admission and camera checks: 30 passed.
- Configured Ruff and mypy (711 files) pass. An accidental `mypy src` invocation included
  excluded untyped desktop modules and produced unrelated errors; the configured gate is authoritative.
- CPU field probe on Ryzen 9 7900X3D (12 physical / 24 logical): four resolution-220 fields,
  one/two/four workers took 4.66/2.64/1.71 s and used 3.02/5.73/11.00 effective cores.
  Each field retained about 301 MB. These direct native measurements do not bypass admission
  in the app; the GUI probe below exercises the actual coordinator.
- Rendered Qt viewport under four coordinated jobs (12 resolution-220 field builds): no
  camera-triggered domain jobs; camera callbacks max 1.83 ms. Frame p95/max 45.56/75.16 ms
  versus idle 40.35/67.15 ms. This synthetic overlapping-cube scene is not a whole-body FPS claim.
  Screenshot inspected; raw results in `build/viewport-worker-review`.
- Native build and six CTests, native style checks and PowerShell checks pass. QML check
  initially failed because its default SDK path is checkout-local; resumed with explicit
  shared SDK path and passed (186 QML files / 46 types, zero API errors). Full pytest is running.
- Camera keyboard/buttons/menu, restore, focus/rebinding, workspace and persistence acceptance
  passed with a resolution-24 setup fixture. The original production-resolution setup exceeded
  that older script's four-second settle deadline before reaching its camera assertions.
- Portable app built from `78c6ad41`; relocated minimal-PATH suite is running. A separate
  packaged camera/mirror command probe passed: zero camera jobs, real rule edit still starts jobs.
- Main-thread/CPU audit and architecture/computation history have been written. They explicitly
  retain synchronous API candidates and note GIL, rendering and atomic-publication limits.

## Next actions

1. Finish the full pytest/numerical/doctor checks and relocated application qualification.
2. Record final evidence, review diff and integrate after validation. Origin/main still at baseline.

## Recovery inputs

Use the shared environment `E:/development/anthroforge/.venv` with explicit PYTHONPATH to
this checkout. Existing native library: `build/skin-pipeline/bin/af_native.dll`; Qt SDK:
`E:/development/anthroforge/.tools/qt/6.12.0/msvc2022_64`. External AVBD checkout at
`E:/development/anthroforge/build/application-boundaries` is read-only and independently dirty.
The root checkout has unrelated assembly work; leave it untouched. Prior local-only probe:
`C:/Users/alexe/.codex/visualizations/2026/11/25/01a21362-f926-7710-8635-1f759dbc0849/job-thread-audit/`.
