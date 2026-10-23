# Skeleton shortcut and driver migration

- Branch: `codex/skeleton-shortcuts-migration`; integration: `main`.
- Base: `2d34278e504c8b6a7f1e1823ba4328e82f022366`.
- Status: inspecting source and mapping; no migrated deliverable yet.
- Updated: 2026-10-23, Europe/Bucharest. Direct desktop work, background only.

## Outcome

Migrate the Blender skeleton's shortcuts and drivers using the qualified 0.3
wrappers, formulas and Parametric engine. The user selected the assembly with all
96 authored muscles. Produce a new versioned copy; preserve geometry, retained
attachments, source files and independent opposite-side construction.

## Inputs and decisions

- Original definitions: `E:/development/WIP_models/skeleton_comb_base.blend`;
  complete inventory: `docs/research/shortcuts_030/inventory.json`.
- Geometry donor: `E:/development/WIP_models/muscle_reconstruction_workflow/runs/
  2026-10-13-serratus-anterior-partial-manual-16c4eea4/serratus_anterior_partial_v001.blend`.
- Destination input: `E:/development/WIP_models/muscle_reconstruction_workflow/runs/
  2026-10-21-standalone-four-muscle-transfer-afcbd2ec/skeleton_four_muscles_v001.anthroforge`.
- 105 source shortcuts and 34 driver channels. Source rib/pelvic guides are
  four-point Bezier loops, not analytic circles; replacing them blindly changes shape.
- No live symmetry, mesh fallbacks, source mutation or forged accepted results.
  Use shared application operations. Runtime changes require demonstrated defects.
- Preserve unrelated root `__init__.py`.

## Next steps and acceptance

Inspect the actual donor definitions and current target records. Map all controls,
units, local/world frames, uniform vectors and attachment policies. Qualify baseline
geometry/attachment preservation, representative edits and restoration, reopening,
and hidden rendered views. Record explicit differences and unresolved items rather
than claiming migration from successful API calls alone.

## Current checkpoint

- External run: `E:/development/WIP_models/shortcut_migration_030_20261023/`.
  It contains the immutable input copy, read-only donor extraction, probe script
  and captures. Original/donor inventories agree except small transform values;
  the current assembly remains the placement authority.
- `tools/skeleton_shortcut_migration.py` exposes all 80 saved digit controls through
  shared operations. `digits-checkpoint.anthroforge` is an incomplete checkpoint,
  not delivery. All non-shortcut document fields compare exactly unchanged.
- Required user choice pending: preserve existing Bezier guides and drive their
  controls, or extend Parametric to preserve Bezier construction. The current
  Parametric output is polyline; matching all 48 path positions still changes
  frames and the closed-body start. Probe observed actual pelvic shape changes.
- A separate real defect blocks safe Hook drivers: numeric channel edits rebuild
  a pure TRS matrix, discarding existing shear. Writing the same scale value to
  `hook:femur_knee_hook` changed a matrix component by 5.8497. Native partial-channel
  editing now preserves the affine basis, with exact no-op handling at the shared
  property boundary. Build/tests underway; not yet release-qualified or packaged.

## Expanded checkpoint (not delivery)

The mapping now covers 96/105 exposed controls, plus hidden Hip Joint local Y/Z and
paired-bone dependencies. Tools are `skeleton_shortcut_migration.py`,
`skeleton_shortcut_controls.py`, `skeleton_shortcut_hooks.py`,
`capture_skeleton_shortcut_frames.py` and `check_skeleton_shortcut_preservation.py`.
Local outputs are `controls-checkpoint.anthroforge` and `hooks-checkpoint.anthroforge`.
They are unqualified intermediates. Source frames are captured in `donor-frames.json`.

Two required product choices remain pending in the chat:
1. Keep the original Bezier guides or extend Parametric to preserve Bezier construction.
2. Preserve Pubis Arc Angle's Ilium override through an explicit policy scope for a
   multi-SCP driver, or retain the confirmed 0.3 rule and omit that override. The
   source angle also controls Sacrum width, which prevents single-SCP ownership.

CH-059's combined Windows gate passed 1,952 tests and five CTests. Subsequent actual
assembly checks observed tessellation changes in two tissue families on recalculation,
with vertex drift below 5e-14; one cropped result changed counts. CH-060 adds compatible
topology retention at base/rest stages; 42 focused tests pass. The new real-assembly
rerun and combined gate remain pending. Preserve failure evidence; do not relax the
geometry/attachment acceptance checks or install these intermediates as delivery.
