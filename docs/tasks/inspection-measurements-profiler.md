# Measurements, repeatable views and explanatory profiling, 0.1.8

- Task branch: `codex/inspection-measurements-profiler`
- Integration branch: `main`
- Starting revision: `089b114180fc1ee6a8493b4dbfb9d6f2f8f6df12`
- Status: implementation in progress
- Active writer: desktop chat, direct work
- Updated: 2026-10-18

## Confirmed outcome

Implement the remaining recommendations 6 (F07/F10) and 7 (B09/I01).
The user selected straight-line distance between two picked surface points, with
XYZ readouts; minimum clearance between complete meshes is outside this request.
Add named, persistent camera bookmarks and include measurement/view evidence in
inspection reports. Keep canonical metres, presentation outside anatomical undo,
and native geometry queries authoritative.

Extend existing runtime reports with invalidation reasons, cache hit/miss/eviction
events and native geometry retention by document, history, jobs and viewport.
Distinct owners may retain the same geometry: report deduplicated allocations and
overlapping ownership explicitly. Do not imply exact process RSS or GPU allocation
coverage. Profiling off must not scan geometry, poll or gather new telemetry.

## Ownership and validation

Use shared application operations and typed persistence records, current camera and
displayed-revision picking, native geometry and the existing coordinator/profiler.
Keep functions within 15 lines; preserve the unrelated root `__init__.py`.
No subagents, additional worker pools, or Blender runtime dependency.

Validate measurement transforms/revisions/deletion, units, bookmarks and save/reopen;
actual pointer and camera interaction, inspection snapshot consistency, bounded
profile summaries/caches, disabled behavior and shared allocation accounting.
Run development gate, GUI acceptance, profiler report inspection, relocated portable
checks, source archive and normal main integration. Push coherent checkpoints.

## Current implementation and next action

Baseline 0.1.7 is clean except the preserved legacy stub. Existing native surface
picking, shared workspace camera, runtime recorder and bounded Body base cache are
available. Coordinator invalidation currently loses its cause. Geometry collection
traces document/history/checkpoint/job references; renderer leases need explicit
observation for accurate shared ownership. Inspect their boundaries, then implement
measurement/bookmark records and profiler observation without altering scheduling.

First increment implemented: native surface witness/distance queries, typed frozen
rulers and camera bookmarks persisted per workspace, shared commands, ruler pointer
workflow and overlays, named view management, report measurements. Display staging
now retains the matching asset/revision metadata with its old visible handle.
Stale/deleted source geometry is explicit; rulers retain values, not geometry payloads.
13 focused/architecture/export tests, strict mypy and native build/CTest passed.
Real GUI picks, bookmark save/restore and export during edits passed; viewport and
report images were visually inspected under `build/inspection-018`. No QML warnings.
Recommendation 7 now implemented: shared revision/invalidation/cancellation causes,
Body base-cache events, native allocation inventory and weak ownership observations
for document/history/checkpoint/jobs/catalogue/cache and displayed/staged viewport
leases. Summaries include bounded explanations, deduplicated totals and overlapping
owner bytes. Observation is recording-only; native AABB capacity is an estimate and
Python/Qt/GPU allocation sizes remain outside coverage. Observer failures are explicit.
The full suite passed (538 tests); a subsequent late-worker/repeated-capture regression
also passed with focused tests. Actual GUI acceptance now includes bookmark restoration
during a modal curve move, unchanged geometry at restoration and one undo action.

Five actual GUI profiler captures now pass (normal/snapped, Activity closed/open,
cancelled gesture); repeated recording and document replacement also pass. Captures
expose input-output invalidation, newer-request cancellation, warm base-cache hits and
document/history/job/displayed ownership. Perfetto imports 31,822 slices and all ten
memory counter tracks without importer errors. Six serial counterbalanced baseline,
dormant and recording trials completed under `build/inspection-018/performance-qualified`.
Idle means were 16.48–16.95 ms/frame, recording 18.36–19.10 ms on the cube/body fixture.
The benchmark wait now uses a real Qt loop: repeated QTest.qWait had starved Python
export while the desktop event loop itself remained functional. No production export
change was needed. Documentation/version and portable acceptance are prepared.

First development gate found one 16-line acceptance function and an overly broad
owner-overlap test assertion (the process registry can include other sessions' meshes).
Both were corrected; focused tests pass. Re-run the gate and final GUI, then build and
check relocated 0.1.8 packaging, source archive and normal main integration. Full task
completion and portable qualification remain pending at this checkpoint.

Final source gate now passes (540 tests and all native/numerical/style checks). Actual
inspection, view-gesture and prior workflow GUI checks pass; ruler category picks are
checked after the frame boundary publishes visibility. Updated PNGs were inspected.
Next build from the clean source checkpoint, run the extended relocated portable gate,
record package evidence, create the source archive and merge/push main normally.

References: Qt 6.12 View3D/pickResult and Perfetto counter tracks documentation were
researched before implementation. Qt bounding-box picks do not replace our native
displayed-geometry picking; trace counters are suitable for byte snapshots.
