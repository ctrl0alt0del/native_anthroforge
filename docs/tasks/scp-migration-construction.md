# Editable SCP migration: Shrinkwrap and segment chains

- Task branch: `codex/scp-migration-construction`
- Integration branch: `main`
- Starting revision: `bfe419c79e8ff3e8cba2c12c83daf538020d7151`
- Status: in progress
- Last updated: 2026-10-21, Europe/Bucharest
- Active writer: desktop migration chat, direct work

## Outcome and acceptance

Implement live Shrinkwrap and a generic parameter-driven segment-chain primitive in
desktop and headless application, then migrate all approved SCPs from the one source
file below. Preserve editable curves, hooks, lattices, hierarchy, placements and
independent mirrored counterparts. No silent mesh-import fallback. Import meshes only
where approved. Inspect actual shapes and reopened saved project, not only API success.

## Decisions and relevant files

- Atlas v002 and all replacement proposals approved. Digits use node-group length,
  thickness, spread and bend controls, not ordinary body-curve editing.
- Spine: curve-deformed capsule. Pubis/Ischium/Ilium: one shared authored guide,
  per-consumer placement/ranges/base shaping.
- Scapula: preserve Simple subdivision, live nearest-surface Shrinkwrap to Ribs,
  local displacement, then thickness. Do not import already wrapped geometry.
- Digits: reproduce saved node graph (including radius profile, cap/frame/sampling,
  zero-length segments and self-union). The unused Knuckle Size socket has no effect.
- Follow engineering guidelines; native C++ numerical work; shared lifecycle/operations;
  maximum 15 physical lines per function; background-only validation.

## Current state

Inspected core primitive/deformer records, evaluation and application operations.
Existing deformer model assumes every deformer has a Hook/Lattice control; Shrinkwrap
needs an explicit geometry target relationship and dispatch-time accepted target data.
Existing BODY is curve-driven; parameter-driven segment construction needs its own
typed definition and evaluator. Native nearest-surface Shrinkwrap now builds and
matches 24 Blender fixtures. Typed target roles, relationships, copy/persistence,
deletion protection, shared commands and inspector are integrated. Desktop rendering
qualification, broader lifecycle checks and migration remain. Segment Chain now has
typed parameters, native geometry, shared commands and a focused inspector. Raw
Index and Big_Toe reference vertices match within 3e-6, including the zero-length
segment. Exact union is integrated; stable material bindings across its changing
triangulation are the next integration requirement before migration acceptance.
Those bindings are now implemented using persisted per-triangle material coordinates;
fibers/anchors and SCP children retain their capture resource and do not recapture.
Simple subdivision and constant local displacement are explicit ordered modifiers;
Body pieces also expose pre-bend subdivision for the approved shaped bases.

## Verification

Source atlas review saved and browser-verified in prior stage. Source SHA256:
`fb199c4f466cb06380e3596d7f83e715dd72abf71b154d703818d4df75832acd`.
Native build/CTest: 5 passed. Focused Shrinkwrap, primitive and lifecycle tests:
53 passed; fixture generator length corrected for architecture recheck.
Full development gate, UI/package and migration not yet run.
Latest focused Shrinkwrap/Segment Chain/architecture run: 36 passed. An exploratory
whole-tree mypy invocation exceeded the configured typed scope and reported existing
dynamic-module errors; use the repository's configured `mypy` command in the gate.
Configured mypy passed. Full pytest at the material-binding checkpoint: 1,635 passed.
Current geometry-stage/segment/shrinkwrap/architecture subset: 18 passed, including
Simple subdivision against Blender and provenance through refinement. The latest
retained-anchor overlay adapter still needs its fresh native build and check.

## Next actions and blockers

Migration work is now under the adjacent external `scp_migration_v001` folder.
The reproducible builder creates all 59 entries (33 originals and 26 independent
counterparts), with no imported-final fallback. `candidate.anthroforge` is **not
accepted/delivered**: initial construction is complete, but anatomy bindings,
visual refinement and interactive/package qualification remain.
Per-stage Blender capture and two-way native nearest-surface comparisons exposed
reversed Segment Chain side winding; corrected to agree with caps. All ten final
digit shapes now agree within ~2e-6 scene units, including Thumb's disabled
zero-length/zero-radius segment. Fixed-length bodies on cyclic guides retain caps.
Rib source GN double placement is explicit in consumer/control frames; connected
loft seams differ intentionally. Scapula follows the live rib result. Ilium uses
the shared pelvic guide plus a dense editable BASE cage; its current maximum
surface discrepancy is ~0.0334 (diagonal ~4.77), not yet shape acceptance.
The new comparison renders required correcting camera mode/fit; only inspect
re-rendered full-frame views. External artifacts must be retained across recovery.

1. Extend typed definitions and owning reference/dependency/persistence boundaries.
2. Native kernels plus compact Blender 5.0.1 parity fixtures and shared UI/API controls.
3. One-off migration and per-SCP numerical/visual comparison; resolve actual mismatches.
4. Reopen, edit propagation, gate, offscreen and canonical portable qualification.

## Recovery inputs

Source: `E:/development/WIP_models/muscle_reconstruction_workflow/runs/2026-10-13-serratus-anterior-partial-manual-16c4eea4/serratus_anterior_partial_v001.blend`.
Adjacent `scp_migration_atlas_v001/` contains `details.json`, `scps.json`, evaluated
NPZ geometry, source images and inspection scripts. `scp_migration_atlas_v002/`
contains revised approved proposals and original review. Keep large anatomy assets
outside Git. Preserve source file and unrelated root `__init__.py`.
Blender: `C:/Program Files/Blender Foundation/Blender 5.0/blender.exe`.
Python: `.venv/Scripts/python.exe`; build: `tools/build-native.ps1`.
