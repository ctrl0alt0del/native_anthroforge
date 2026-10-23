# Skeleton shortcut and driver migration

- Branch: `codex/skeleton-shortcuts-migration`; integration: `main`.
- Base: `2d34278e504c8b6a7f1e1823ba4328e82f022366`.
- Status: complete; artifact and canonical runtime qualified for main integration.
- Updated: 2026-10-23, Europe/Bucharest. Direct desktop work, background only.

## Outcome

Migrate the Blender skeleton's shortcuts and drivers using the qualified 0.3
wrappers, formulas and Parametric engine. The user selected the assembly with all
96 authored muscles. Produce a new versioned copy; preserve geometry, retained
attachments, source files and independent opposite-side construction.

## Delivered copy and qualification

The final copy is
[`skeleton_96_muscles_shortcuts_v001.anthroforge`](E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge).
Use the rebuilt canonical `dist/0.3.0/AnthroForge.dist/AnthroForge.exe`. The original
assembly and Blender sources are unchanged. This is a one-file migration, not a general
Blender-project importer. The checkpoint sections below are historical progress records;
their pending questions/work are superseded by this delivery summary.

- 59 SCPs, 96 authored muscles, 326 Fibers, 105 source-ordered exposed controls,
  66 formulas and 37 controls. All baseline tissue/formula results are ready.
- Six four-knot guides retain Bézier construction under Parametric evaluation.
  Six added Hook/frame controls and three Hook-on-lattice bindings reproduce compact
  pelvic controls. No mesh-import fallback or mirrored muscle was added.
- Pubis Arc Angle retains its temporary Ilium policy through explicit Pubis scope,
  while still being a multi-owner shortcut under All. Saved authored bindings are intact.
- Original/candidate comparison: 619 original records and 1,325 resources, exact mesh
  connectivity and binding payloads, maximum mesh drift 3.397e-12. Accepted path-frame
  differences are separately reported, not claimed identical. Packaged Ilium edit,
  undo and save compare all 625 output records and resources with zero drift in mesh,
  paths, frames and poses.
- The full Windows gate passes 1,970 tests and five CTests. After two additional smoke
  readiness tests, the final regression run passes 1,972 tests. Style/function limits,
  typing, numerics, Qt-free headless and the complete minimal-PATH portable suite pass.
  Actual packaged desktop opening verifies all 59 SCPs and no QML/scheduler warnings.
- Offscreen loaded UI and production interpolation/policy editors were inspected.
  Software offscreen UI does not render the 3D viewport; separate hidden native GPU
  captures verify geometry. Blender/native edited pelvis views were visually compared;
  the existing skeleton approximation remains, rather than exact Blender vertex parity.
  No physical interactive acceptance or GPU execution timing is claimed.

### Evidence and existing attachment limits

External evidence is under `E:/development/WIP_models/shortcut_migration_030_20261023/`:
`delivery.json`, `delivery-preservation.json`, `source-native-shapes.png/.json`,
`delivery-front.png/.json`, `compact-edits/`, `blender-edits/` and `failure-15.json`, `failure-16.json`,
`failure-21.json`. The latter compare the same edits in immutable input and candidate:
Humerus/Radius length +5% produces the same FDS radial cropped-material failures;
Thumb metacarpal thickness +0.05 (about +71%; previously mislabeled +5%) produces the same seven union-covered fiber bindings.
These are preserved pre-existing limitations, not silently rebound or classified as
successful edits. Other tested controls settle successfully and full-resource undo passes.

The final saved revision 57463 was rendered by the packaged executable with no visible
window and no warnings: 254 chunks, 2,012,808 vertices, finite geometry. The resulting
`delivery-front.png` was visually inspected, confirming the complete authored-side
musculature and preserved opposite-side skeleton context.

Local build evidence: `build/skeleton-shortcuts-qualified-gate.log`,
`build/skeleton-shortcuts-final-pytest.log`, `build/skeleton-shortcuts-portable/portable-check.json`,
`build/skeleton-shortcuts-real-portable/desktop.json` and
`build/skeleton-shortcuts-real-portable/roundtrip-preservation.json`.
The source-equivalence checks also cover compact Hook versus dense coordinate-formula
Ilium edits (maximum mesh drift 1.954e-13). Their observed 13.20→1.18-second edit time
is one controlled workload, not a broad performance guarantee.

### Ownership and coupling review

The coordinator directly reviewed the changes separately from test results. C++ owns
affine channel edits, Bézier interpolation, path/frame sampling and deformation. Typed
core records own interpolation settings, explicit policy references and immutable formula
indexes. The application owns validation, temporary edit contexts and dependency-aware
batching; the existing coordinator retains reservations, capture, cancellation and
publication. UI editors call shared operations and expose shared lock reasons.

One-off migration orchestration remains in `tools/skeleton_shortcut_*`; pelvic mapping
uses existing Hook-on-lattice evaluation rather than a new production skeleton evaluator.
No native handles are serialized, no competing worker pool is added, no Python optimizer
or per-sample production callback is introduced, and material bindings are not silently
rewritten. The rejected dense point-formula experiment remains explicitly identified in
the evidence. The smoke readiness change affects diagnostics, not user loading policy.

### Delivery

The canonical portable folder and companion `dist/AnthroForge-0.3.0-source.zip` include
the qualified runtime, current documentation and reproducible migration tools. Large
anatomy files and local captures remain in the external folder, not Git. Final fetch
found no newer main changes requiring reconciliation. Integration uses a normal merge
and push preserving all task checkpoints. The unrelated root `__init__.py` is untouched.

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

## Initial steps and acceptance (historical)

Inspect the actual donor definitions and current target records. Map all controls,
units, local/world frames, uniform vectors and attachment policies. Qualify baseline
geometry/attachment preservation, representative edits and restoration, reopening,
and hidden rendered views. Record explicit differences and unresolved items rather
than claiming migration from successful API calls alone.

## Initial checkpoint (historical)

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

## Actual override edit correction

Compact baseline passed (original 619 records / 1,325 resources, max mesh drift
3.397e-12; only six declared controls and three Hook bindings added). Ilium-angle
edited outputs match the coordinate-formula reference within 1.954e-13. The compact
mapping is selected; no geometry fallback. Source Blender change captures are in
`blender-edits/` and the source SHA remains unchanged.

Testing Pubis Arc Angle exposed a wait cycle caused by pose batching ignoring its
temporary Surface Nearest override. `wait-diagnostic.json` records an acyclic port
graph but cyclic batch wait. CH-064 extends the existing policy adapter into batch
planning. The small failing regression now passes and actual control 10 settles.
Remaining representative edits run in `build/skeleton-shortcuts-edits-second.log`.
The previous full gate had 1,968 passing tests and one temporary-tool function-length
failure; that failure is fixed. Rerun the final gate after all changes. Portable build
and final saved delivery remain pending. Root `__init__.py` untouched.

## Final candidate and runtime checks

`skeleton_96_muscles_shortcuts_v001.anthroforge` exists in the external migration
folder: 59 SCPs, 96 tissues, 326 fibers, 37 controls, 105 exposed source controls and
66 formulas. Controls are ordered as in the donor. All formulas/tissue results are
ready; no active temporary edit context is saved. Original assembly/Blender hashes
remain unchanged. Final preservation check passes at max mesh drift 3.397e-12 with
exact retained bindings/connectivity. Packaged edit/undo/save round trip compares
all 625 records and 1,325 resources with zero geometry/path/pose drift.

The Windows gate passes 1,970 tests and five CTests. The full portable suite passed.
Production interpolation/scope QML passed offscreen after correcting its global
authoring-adapter reference. Native hidden capture of the complete assembly and
Blender/native pelvis comparisons were visually inspected. Source-shape differences
remain at the prior skeleton approximation level; see `source-native-shapes.json`.

Actual Humerus/Radius length +5% and Thumb metacarpal thickness +0.05 (about +71%; previously mislabeled +5%) encounter retained
material attachment errors. Independent edits in immutable input reproduce the same
affected fibers and errors exactly (`failure-15/16/21.json`). These are preserved
pre-existing crop/union limitations, not silently rebound or relabeled as migration
success. Other tested controls and full-resource undo complete.

Large-project GUI smoke exposed a validation defect: the two-second capture ran
before asynchronous Open finished. Smoke now waits for document, tasks and staging,
reports entity count, and fails after a bounded deadline. New readiness tests pass.
Final repackage, loaded-desktop qualification, documentation/source archive and merge
remain pending. Do not claim the old empty/loading screenshot as a loaded-GUI pass.

## Completed final qualification (supersedes the preceding checkpoint)

The rebuilt canonical executable passes the complete portable suite and the actual
assembly's control-edit/undo/save workflow. Final source regression: 1,972 passing tests.
Loaded desktop smoke reports 59 SCPs and no warnings; the new screenshot was inspected.
The separate packaged native render of final revision 57463 was also inspected and is
complete. The repeated saved round-trip comparison reports zero differences for all
625 records / 1,325 resources. Documentation links and changed-file whitespace checks
pass. Delivery, evidence, existing limits and ownership review are summarized above.
