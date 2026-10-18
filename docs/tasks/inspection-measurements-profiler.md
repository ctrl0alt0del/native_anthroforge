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
Full regression/release checks and recommendation 7 remain pending.

Next implement bounded invalidation/cache/memory observations, tests and profiler
acceptance. Then finish gesture/visibility regression, documentation, 0.1.8 packaging
and normal main integration. Do not mark the whole task complete from this increment.

References: Qt 6.12 View3D/pickResult and Perfetto counter tracks documentation were
researched before implementation. Qt bounding-box picks do not replace our native
displayed-geometry picking; trace counters are suitable for byte snapshots.
