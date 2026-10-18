# Measurements, repeatable views and explanatory profiling, 0.1.8

- Task branch: `codex/inspection-measurements-profiler`
- Integration branch: `main`
- Starting revision: `089b114180fc1ee6a8493b4dbfb9d6f2f8f6df12`
- Status: complete
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

## Delivered and validated

Both recommendations are delivered in 0.1.8. Typed workspace rulers freeze two surface
witnesses with XYZ/delta/distance and explicit stale status; named cameras preserve
projection and ongoing edits. Native measurement queries and displayed-revision picking
serve shared GUI/headless operations. Projects and frozen reports preserve this evidence.

The runtime recorder now captures shared revision/invalidation/cancellation causes,
Body base-cache reuse/eviction and deduplicated native allocation ownership. Weak job
and viewport observation does not extend mesh lifetime. Owner totals overlap; AABB
capacity is estimated. Python/Qt/GPU allocations and transient peaks remain outside
coverage. Disabled profiling performs no new inventory queries or cache collection.

Validation:
- Development gate passed with 540 tests; the final full suite passed 541 after adding
  an explicit native world-coordinate and 3-4-5 distance contract.
- Actual GUI: surface picks, category filtering, m/cm/mm XYZ/distance, stale witnesses,
  bookmark Go during a modal curve move, one undo action and frozen report export.
  Existing axis/restore/gizmo/snap and prior workspace workflows also pass.
- Five complete desktop gesture profiles cover normal/snapped input, Activity open/closed
  and cancellation. Repeated recording/document replacement pass. Perfetto imported
  31,822 slices and ten memory tracks without importer errors.
- Six serial counterbalanced none/dormant/record trials: idle mean frame intervals
  16.48–16.95 ms; recording 18.36–19.10 ms on the cube/body fixture. These do not certify
  full-body performance or zero dormant overhead.
- Final relocated executable passed every portable check with minimal PATH, including
  headless/desktop profiles, project round-trip and image reports. Packaged ruler image
  visually verified: 1.41421356 m diagonal displayed as 1414.214 mm.
- Ownership/coupling reviewed separately from tests; see development_status.md.

A visual check caught inverted ruler display-unit conversion in the first packaged
candidate, despite correct stored coordinates. That candidate was replaced after the
m/cm/mm GUI regression and repeated gesture checks passed. The benchmark wait was also
corrected to use a real Qt loop: repeated QTest waits had starved Python export; production
export did not need a change.

Qualified executable: dist/0.1.8/AnthroForge.dist/AnthroForge.exe
Build source: d005bda595c57c745c87738879b9b238308227fb (clean tracked source).
Executable SHA-256: abe23810632bbe72b3381b46f992489bfc5f638d59756d24533a0d1cdad5ad28.
Later changes are validation tests and release documentation only.
Companion source: dist/AnthroForge-0.1.8-source.zip.
Local evidence: build/inspection-018, especially portable-final and profiles.
Source/continuity records are committed and pushed; binaries/captures remain local.
The unrelated root __init__.py is preserved.

References: official Qt 6.12 View3D/pickResult and Perfetto counter-track documentation
were researched before implementation. Native displayed-geometry picking remains authoritative.
