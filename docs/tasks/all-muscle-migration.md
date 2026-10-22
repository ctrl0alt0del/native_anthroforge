# All available authored addon muscles on the migrated skeleton

- Branch: `codex/all-muscle-migration`; integration `main`; base `b642ce5`.
- Status: complete. Authored-only v002 is installed at the existing project path;
  preservation, normal reopen, all 96 source comparisons and packaged views pass.
- Request: migrate accepted and awaiting-review builds into the same project as the
  prior four families. Latest correction also removes the four existing mirrored
  tissues; mirrored skeleton SCPs remain. No rejected/unstarted/held cases were constructed.
- Run: `E:/development/WIP_models/muscle_reconstruction_workflow/runs/2026-10-21-standalone-all-muscle-transfer-958f7969/`.
- Destination remains the prior run's `skeleton_four_muscles_v001.anthroforge`.
  Original recovery copy: `inputs/four-muscles-before.anthroforge`.
- Qualified candidate: `candidates/skeleton_all_authored_muscles_v002.anthroforge`.
  The original v001 and `qualification.json` retain the complete migration evidence;
  `checks/mirror-removal.json` qualifies the authored-only revision 51454.
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

## Original v001 delivery (superseded by the authored-only follow-up)

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

## Authored-only follow-up (2026-10-22)

The user's delayed clarification explicitly authorizes removing the four mirrored
muscles retained in v001. The existing deletion API removed their four tissues, four
membranes and eleven fibers. All SCPs, including mirrored bones, and every authored
muscle remain. No production code changed.

`tmp/remove_existing_mirrors.py` works from `inputs/before-mirror-removal.anthroforge`
and creates `candidates/skeleton_all_authored_muscles_v002.anthroforge`. It verifies
all remaining authored records/geometry, one-action undo grouping, normal reopening
and the existing 96-source comparisons. The requested delivery path remains unchanged;
replacement followed these checks and offscreen inspection. Prior v001 evidence is
immutable historical evidence; final follow-up results are in `checks/mirror-removal.json`.

Deletion follows consumer-before-provider order: mirrored TFL and Pronator construction
references other removed mirrored tissues. No retained object refers to the removed
graph. The result has 59 SCPs, 96 tissues, 96 membranes and 326 fibers. All 619 retained
records pass authored-data comparison; all 96 source geometry comparisons pass after
normal opening. Retained mesh position drift is at most 1.757e-12 scene units; path
position/radius/tilt drift is at most 1.557e-13. Path material parameters also pass.

The initial diagnostic compared all 11 sampled-path columns and found regenerated
tangent/normal differences on 21 fibers. These are explicitly recorded separately:
they are not positional changes, and all actual consumer meshes remain within the
strict 1e-8 preservation tolerance. Full derived-frame identity is not claimed.
The exact cause of frame variation is not established by this data-only task.

`tmp/qualify_mirror_candidate.py` qualifies the saved candidate without resaving it.
`tmp/install_authored_only.py` renders the canonical executable offscreen, then requires
a separately invoked, locked/hash-checked atomic installation. The recovery copy is
`inputs/before-mirror-removal.anthroforge`. No full development gate or runtime rebuild
is necessary for this document-only edit; previous release checks remain historical.

Front/back packaged renders were inspected by the coordinator; no windows were
shown. `checks/mirror-removal-views.json` records that evidence and its limits.
`delivery-authored-only.json` records atomic replacement of the original destination
with SHA256 `2bcd72212488a5ea5ca4a19f2d5d2900a9ff9a814560156203f42e3721bf07b6`.
The run manifest, muscle skill and practical lesson r3 reflect the authored-only
delivery. Existing approval statuses and all earlier scope limits remain unchanged.
