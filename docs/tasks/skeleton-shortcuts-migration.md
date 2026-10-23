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

## Approved extensions and recovery state, 2026-10-23

The user chose Parametric with preserved Bezier construction, and an explicit
attachment scope for multi-SCP controls. These supersede the pending alternatives
above. Inferred ownership remains unchanged. Implementation adds interpolation and
per-segment sampling, retaining knot IDs, handle modes and offsets, plus a separate
validated policy scope. Desktop/API, persistence and copying share these records.

The 96-control checkpoint passes the complete local comparison: 619 records,
1,324 resources, identical mesh connectivity and retained attachment payloads;
maximum coordinate drift 3.746e-12. Path frame differences are separately reported
(up to 0.302), without surface geometry changes. This remains an intermediate.
Nine source controls remain to integrate. Actual-guide, complete migration,
GUI/portable qualification and final packaging remain pending.

A one-ULP driver decomposition change previously triggered attachment recapture.
Transform channel no-op comparison now uses eight ULPs, without an absolute
geometric tolerance. Tiny real edits remain active. Focused tests pass.
Prior combined gate: 1,954 tests/five CTests; latest extensions: 21 tests passed.


## Guide conversion and remaining parameter wiring

`tools/skeleton_shortcut_guides.py` converts six actual guides using four generated
Bezier knots at the original per-segment resolution. The shared `curve.engine`
operation accepts optional typed settings atomically; equivalent sampling keeps
existing topology locks intact. Actual 96-muscle guide comparison passed: identical
mesh topology and retained bindings, max mesh drift 1.041e-12 against the 96-control
checkpoint. Raw artifact: `guides-checkpoint.anthroforge`, still not delivery.

Additional shared correction: read-only formula guards use the same transform
roundoff equivalence as numeric edits, so normal attachment pose evaluation cannot
fail because of a one-ULP scale decomposition change. A read-only world
`volume_scale` input reproduces Blender's signed cube root of determinant (5.0.1
`fcurve_driver.cc` SCALE_AVG), including shear/reflections; native tests pass.

Remaining scripts are radius/shape wiring, unqualified: `skeleton_shortcut_radius.py`,
`skeleton_shortcut_formulae.py`, `skeleton_shortcut_pelvis.py`, and
`skeleton_shortcut_pelvic_stage.py`. Radius stage currently runs with a 600-second
bound and a profiler capture; the prior 120-second bound expired. Do not interpret
successful submission as geometry acceptance. The radius stage creates remaining
virtual inputs; pelvic stage connects the pre-bend cage formulas and Ilium override.
Mirrored counterpart parameters remain independent: no new mirrored muscle objects
and no shared driver outputs for mirrored bone controls. The early radius checkpoint
may contain mirror-guide outputs; pelvic-stage cleanup removes those explicitly.

Next: complete and qualify radius/pelvic stages; compare retained state and all
geometry (allow only declared guide engine/consumer-mode changes); qualify actual
control edits and restoration against donor semantics; inspect hidden rendered views.
Then complete documentation, combined gate, canonical portable package/source archive,
and validated main merge. No final project has been delivered.

## Formula-barrier correction and radius preservation

The 600-second radius timeout was reproduced on two drivers plus a queued attachment
pose, despite an acyclic output graph. CH-062 partitions formula batches around
evaluated-output barriers, preserving coherent groups and coordinator ownership.
Regression and focused formula/policy tests pass, including explicit Manual work.
The new radius run completed. `radius-preservation.json` compares all 619 records
and 1,325 resources against immutable input: identical connectivity and attachment
payloads; max mesh drift 3.397e-12. Only the declared six guide definitions and four
curve-consumption frame/mode changes are allowed by the migration comparison tool.

`pelvic_stage` is now running from that checkpoint. No final delivery or main merge.
Pending: qualify full mapping and parameter edits, actual shapes, extension docs,
full gate and canonical portable build. Preserve unrelated root `__init__.py`.

## Complete controls and compact pelvic mapping under qualification

All 105 source controls are wired in `pelvic-checkpoint.anthroforge`; exact retained
bindings/connectivity and baseline meshes passed (`pelvic-preservation.json`). The
Ilium-angle edit and undo work, but 1,740 point-coordinate formulas made this control
take 13.20 seconds to settle. Snapshot indexing and a scale-specific dependency
correction are covered by CH-063 and regressions. The 1,964-test/five-CTest gate passed
before the latest small changes; final combined checks remain required.

The existing Hook-on-lattice contract supports a more compact migration. The new
`skeleton_shortcut_pelvic_hooks.py` adds a fixed affine frame and driven Hook for each
of Pubis/Ischium/Ilium, retaining the original cages and shared guide. The experiment
reduces the pelvic section to 25 formulas. `compact-checkpoint.anthroforge` is still
an intermediate. Same Ilium edit settled in 1.18 seconds, undo passed. Full equivalence
and baseline checks are running. Outputs/profiles remain in the external migration
folder, `compact-edits/`; the old point-formula results are retained as evidence.

Production QML interpolation/scope controls passed offscreen inspection, including
readable screenshots. New sampling lock presentation needs final focused coverage.
Next: compare compact mapping, representative edits and source semantics; inspect
actual shapes; finalize source-order controls and final copied project; combined gate,
canonical portable/source build; validated merge/push. No final file delivered yet.
