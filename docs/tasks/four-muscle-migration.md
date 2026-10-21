# Four random addon muscles on the migrated skeleton

- Branch: `codex/four-muscle-migration`; integration: `main`; original base: `a8022a4`.
- Status: implementation, artifact delivery and qualification complete; validated merge/push next.
- Scope: inventory existing workflow muscles and reproduce four randomly selected families
  as editable construction and inflation in a copy of the migrated standalone skeleton.
- Originals, catalogue acceptance states and unrelated root `__init__.py` are unchanged.

External run:
`E:/development/WIP_models/muscle_reconstruction_workflow/runs/2026-10-21-standalone-four-muscle-transfer-afcbd2ec/`.
Final copy: `skeleton_four_muscles_v001.anthroforge`, saved revision 2001.
Searchable inventory and actual source/native comparisons: `muscle_inventory.html`.
These anatomy artifacts are local-only and are deliberately excluded from Git.

Catalogue revision 181 has 149 entries: 17 accepted, 70 ready for review, 56 not
started, four needing rebuild and two needing reverification. Existing source files
and representative filtering yield 70 distinct eligible types (17 accepted, 53 pending).
Random seed `3257324722672619128`, no rerolls: flexor carpi radialis, sartorius,
pronator teres and tensor fasciae latae. Both sides give 8 TissueVCPs, 8 Membranes,
22 Fibers and all 59 original SCPs. Mirrored counterparts are independent.

## Observed gap and shared repair

Matching addon Free paths did not preserve the loft. Arclength reassignment increased
FCR from 325 to 6494 vertices and changed TFL inflation by .315 scene units. Optional
identity-qualified material stations now belong to SurfaceAlignment; C++ maps evaluated
path parameters to stations. `surface.correspondence` uses existing policies/jobs.
Persistence and copying preserve/remap point identities; missing points fail explicitly.
Realign deliberately resets correspondence. Unsupported range/closed/uniform/branched
uses cannot silently discard it. Default surface behavior is unchanged.

The one-off transfer retains donor transverse density and selects tissue resolution 3,
which adds no refinement to these already denser source grids. Exact POLYLINE paths
preserve the saved addon Free display paths. Bone targets, profile settings, side
orientation, opposite sides and TFL crop are retained. No final muscle mesh import,
Python numerical fallback or alternate muscle evaluator was introduced. CH-031 records
this change in [computation history](../computation_history.md).

## Evidence and limits

- `selection.json` freezes inventory, source hashes, random draw and source review limits.
- `capture/` holds actual Blender RNA, evaluated paths/meshes, material charts and bones.
- `comparison.json`: all eight inflated outputs within 6.4e-7 scene units with matching
  vertex counts; actual comparison images inspected in `views/`.
- `qualification.json`: bone movement, eight inflation edits and eight Fiber edits
  propagate; undo restores geometry. Normal reopen drift is at most 1.34e-13.
- `attachment-audit.json`: 44 endpoints bound to explicitly corresponding SCP surfaces;
  retained endpoint gaps reach .000352 scene units. Original triangle indices are not reused.
- `review.json`: final scoped qualification. `views/packaged-front.png` is the actual
  installed viewport at saved revision 2001, finite geometry, no warnings/window shown.
- Windows development gate passes; final suite 1655 tests, five native CTests,
  native/Python style and mypy. Portable minimal-PATH/offscreen suite passes.
- Installed executable recalculates all 38 new construction/tissue targets, saves a
  separate qualification copy and leaves the delivered project unchanged.
- One canonical `dist/0.2.3/AnthroForge.dist`; runtime code identity `12992dd`.
  Companion source archive includes the final documentation.

Review of ownership/coupling: authored policy belongs to SurfaceAlignment/shared operations;
point-ID resolution stays at preparation, station evaluation is native, owned buffers retain
ctypes lifetimes, and the existing scheduler/result/persistence mechanisms are reused.
The importer remains disposable code under the external run, not a production feature.

All visual review was background-only and coordinator-authored. No interactive acceptance,
arbitrary-pose or inter-muscle packing certification. Sartorius/TFL anatomical reviews
remain pending; TFL femoral pins are retained construction proxies, not an IT-band insertion.
Original .blend files and migrated skeleton retain their hashes. The reconstruction skill
and immutable lesson `standalone-muscle-material-correspondence-20261022` r1 were updated.

## Reproduction

One-off `tmp/extract.py` captures Blender without saving. `tmp/transfer.py` builds through
shared operations; `tmp/compare.py`, `tmp/qualify.py`, `tmp/attachments.py`, and
`tmp/portable_project.py` record actual acceptance. Do not rerun the random draw or
replace the frozen final artifact just to regenerate documentation.
