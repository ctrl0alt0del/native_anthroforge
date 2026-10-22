# All available authored addon muscles on the migrated skeleton

- Branch: `codex/all-muscle-migration`; integration `main`; base `b642ce5`.
- Status: complete. The qualified assembly is installed at the requested existing
  project path; full source/edit/persistence/packaged checks pass.
- Request: migrate accepted and awaiting-review builds into the same project as the
  prior four families. Latest correction excludes new mirrored copies. Four existing
  mirrored tissues are preserved. No rejected/unstarted/held cases were constructed.
- Run: `E:/development/WIP_models/muscle_reconstruction_workflow/runs/2026-10-21-standalone-all-muscle-transfer-958f7969/`.
- Destination remains the prior run's `skeleton_four_muscles_v001.anthroforge`.
  Original recovery copy: `inputs/four-muscles-before.anthroforge`.
- Qualified candidate: `candidates/skeleton_all_authored_muscles_v001.anthroforge`.
  `qualification.json` records revision 51435, source hashes, edits and reopen.
- Direct coordinator work; background/offscreen only; no agents or source .blend edits.

## Result and preserved scope

Frozen catalogue revision 181 contains 87 entries (17 accepted, 70 awaiting review)
across 74 source files. Multi-part families and repeated instances yield 96 authored
TissueVCP units; four were present already, so 92 are new. All are editable native
Fibers/Membranes/Tissues, including biceps/deltoid branches and FDS tissue supports.
There are no final mesh substitutes, invented anatomical approvals or new mirrors.
Source paths, authored charts, side/profile settings, crop and support target intent
are retained. Native dense fields are recaptured against donor target sets; donor
per-node weights are not copied verbatim. Original construction proxies remain,
including rectus offsets near 3.84 scene units. Arbitrary-pose and assembled-body
packing/collision acceptance are outside this technical transfer.

## Shared defects repaired

- CH-032: native surface queries filter unusable triangles and use stable oriented
  barycentrics; original polygon/triangle identities remain explicit.
- CH-033: existing branch evaluation accepts retained authored material stations.
- CH-034: initial generated quad and intrinsic-surface tessellation uses the qualified
  Blender rule; subsequent deformation retains compatible accepted connectivity.
- CH-035: profile boundary poles are classified before normal propagation; material
  cropping has its own addon-compatible triangulation, separate from display splits.
- CH-036: creation/editing share dense Fiber support policy. Skeletal fields exclude
  unrelated tissues; explicitly tissue-backed fields use selected parents. The
  migration recaptures 315 new fields using each donor's recorded support set.

All numerical changes remain native C++; Python owns input policy and orchestration.
No competing scheduler, numerical Python fallback, or source-family condition was
introduced. Ownership/coupling reviewed separately from tests: mesh preparation,
material cropping, profile direction policy and Fiber candidate selection retain
separate responsibilities, with existing coordinator publication and resource ownership.

## Evidence

- `checks/reopen-comparisons.json`: all 96 units pass two-way vertex AND triangle-
  centroid surface checks. Maximum tissue/base distances are 9.56e-7/9.65e-7;
  maximum actual path coordinate difference is 2.44e-11 scene units.
- `qualification.json`: three bone edits and five Fiber edits change geometry;
  undo returns it exactly. Saved normal reopen drifts at most 1.76e-12.
- `checks/preserved-original.json`: all 139 original authored objects preserved.
  Six Boolean-generated bone meshes reorder faces but retain identical oriented
  polygons/triangles and vertices. The previously recorded two source tessellation
  corrections remain explicit. Source .blend hashes are unchanged.
- `checks/attachment-audit.json`: 662 explicit bindings checked against donor targets,
  roles and offsets. `checks/source-support-recapture.json` records dense target sets.
- `views/final-pairs/sheet-00.png` through `sheet-07.png`: all 96 actual donor/app pairs
  directly inspected by coordinator. Source faceting and shape limitations retained.
- Development gate native build/style, five CTests and script-style pass in
  `build/all-muscle-final-gate.log`. One old test assumed implicit tissue support;
  its fixture now explicitly binds the tissue, preserving its publication-frontier
  purpose. Complete rerun: **1669 tests pass**, ruff/format/mypy, numerical boundary
  audit and doctor in `build/all-muscle-final-python-gate.log`.
- Canonical `dist/0.2.3/AnthroForge.dist` rebuilt at runtime code `9d444a3`;
  `build/all-muscle-final-portable.log` passes the full hidden/offscreen suite.
  Later commits change docs/test setup only. No interactive desktop acceptance claimed.

## Delivery

- Installed executable recalculates 518 objects through 11385 recorded jobs, with
  no failed jobs. `checks/packaged-comparisons.json` passes all 96 source comparisons.
  All three actual `views/assembly-*.png` viewports were inspected offscreen.
- `review.json` freezes coordinator evidence and limits. Practical lesson
  `standalone-muscle-material-correspondence-20261022` r2 and the muscle skill are
  updated. Matching final context/usage receipts are stored under `knowledge/`.
- `tmp/deliver.py` locked and hash-checked the original before atomic replacement.
  `delivery.json` records the installed hash and recovery path. The final document
  contains 59 SCPs, 100 tissues, 100 membranes and 337 fibers, including the four
  pre-existing mirrored tissues. There are no new mirrored copies.
- Production fixes and task context follow normal checkpoint/push/validated merge
  to main. One canonical 0.2.3 distribution and companion source archive remain.

All scripts/captures/candidates are in the external run, not production. Preserve
unrelated root `__init__.py`. Do not run competing writers or overwrite source files.
