# Viewport responsiveness and worker ownership

- Task branch: `codex/viewport-worker-responsiveness`
- Integration branch: `main`
- Starting revision: `60b64ec4`
- Status: complete; merged and pushed to main
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

The baseline coordinator had two worker threads. Capture, admission, publication and UI
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
coordinator's original two workers therefore did not imply two-core execution for every operation.
The default pool now admits up to four jobs, bounded by CPU count minus one logical CPU
of headroom. Native-team and memory demands remain shared across editing contexts. Final
deformation now reserves its four-thread quality kernel. This is admission headroom, not
OS affinity or a hard limit on external numerical processes.
DraftBuilder also owns CPU estimates: FIELD claims four and AVBD claims exclusive capacity.
The captured job configuration controls that claim; pending UI builder selection cannot change it.

## Verification

- Complete Python run: **2,991 passed, two failed** in 983.01 s (2,993 collected).
  Both failures exposed suppressed document-change notifications. The application contract
  is restored; SkinPanel filters unchanged eligibility before signaling QML. The final
  affected group, including both failures and all new admission/view regressions, passes
  **70 tests**. This is a complete run followed by verified corrections, not a second clean full run.
- Ruff/format, function-length review, configured mypy (711 files), lock consistency,
  native build, six CTests, native style and PowerShell checks pass. QML validation passes
  (186 files / 46 model types, zero API errors), as do numerical-boundary and native doctor checks.
  QML initially needed an explicit shared SDK path; the checkout-local default was absent.
- Production Qt acceptance passes FIELD builds, Draft/Final switching, retained topology,
  pending settings, AVBD failure/Retry, stable status and extended reopening. UI captures inspected.
  Camera restore/keyboard/buttons/menu/focus/workspace/persistence acceptance passes with a
  resolution-24 fixture. Its older production fixture exceeded the four-second setup deadline.
- Final 256-cube event-loop probe: camera jobs **7 to 0**, maximum tick **162.29 to 2.12 ms**,
  p95 **93.14 to 0.79 ms**. This probe has no rendered frames.
- CPU probe on Ryzen 9 7900X3D (12 physical / 24 logical): four resolution-220 fields with
  one/two/four workers took **4.66/2.64/1.71 s**, using **3.02/5.73/11.00 effective cores**.
  Each field reports about 301 MB. These are single direct-native batches, not universal speedups.
- Final rendered probe during four coordinated jobs: zero camera jobs, camera callbacks max
  **1.85 ms**, frame p95/max **47.94/78.30 ms** versus idle **37.56/72.12 ms**. Screenshots
  inspected. The synthetic overlapping-cube fixture does not establish whole-body performance or 60 FPS.
- Complete relocated minimal-PATH portable suite passed at `e2bd01e5`, including skin fitting,
  painting, mirroring, reports, assembly, persistence and hidden rendering. After the notification
  correction, rebuilt `79371b77` passed focused minimal-PATH native-window/primitive/render,
  project-adoption/recovery, zero-camera-job and full AVBD Draft/Final/update qualification.
  Final packaged camera changes start zero jobs; a real mirror-rule edit starts three.
- Existing AF-41 symmetry behavior was outside scope. Native numerical algorithms are unchanged.

## Delivery and integration

Runtime source revision: `79371b77`. Final portable executable (local-only):
`E:/development/anthroforge/dist/0.4.3/AnthroForge.dist/AnthroForge.exe`.
Promoted from the qualified `build/viewport-ready/AnthroForge app` package and checked
at the canonical destination; see [delivery record](canonical-dist-delivery.md).
The audit, diagrams, remaining synchronous candidates and CPU limits are in
[main_thread_cpu_audit.md](../main_thread_cpu_audit.md); computation record is CH-098.

Qualification is complete. Merged and pushed to main as `042807de` on 2026-11-27.
The unrelated dirty root checkout and the external AVBD runtime are unchanged.

## Local evidence

- `build/viewport-responsiveness`: gate, corrections, native/doctor, CPU and portable logs.
- `build/viewport-worker-review`: final rendered probe and screenshot.
- `build/viewport-skin-gui-review`: production mode/status/Retry screenshots.
- `build/viewport-final-review`: complete portable qualification before notification correction.
- `build/viewport-release-review`, `viewport-release-camera-review`, `viewport-release-skin-review`:
  final executable qualification, native-window screenshots and receipts.
- Prior baseline probe location is below. Generated packages, environments and raw outputs are ignored.

## Recovery inputs

Use the shared environment `E:/development/anthroforge/.venv` with explicit PYTHONPATH to
this checkout. Existing native library: `build/skin-pipeline/bin/af_native.dll`; Qt SDK:
`E:/development/anthroforge/.tools/qt/6.12.0/msvc2022_64`. External AVBD checkout at
`E:/development/anthroforge/build/application-boundaries` is read-only and independently dirty.
The root checkout has unrelated assembly work; leave it untouched. Prior local-only probe:
`C:/Users/alexe/.codex/visualizations/2026/11/25/01a21362-f926-7710-8635-1f759dbc0849/job-thread-audit/`.
