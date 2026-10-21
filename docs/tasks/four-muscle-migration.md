# Four random addon muscles on the migrated skeleton

- Branch: `codex/four-muscle-migration`; integration: `main`.
- Base: `a8022a4`; status: source-side parity qualified, mirrors/lifecycle/release in progress.
- Request: inventory existing workflow muscles, select four randomly and reproduce
  editable fibers, membranes and tissue inflation in a copy of the migrated skeleton.
- Preserve original Blender files, migrated skeleton and catalogue acceptance states.
  No final-mesh muscle substitute. Work directly, background/offscreen only.

Catalogue revision 181 has 149 families: 17 accepted, 70 ready for review, 56 not
started, four needing rebuild and two needing reverification. Existing source files
and representative-type filtering yield 70 eligible distinct built types (17 accepted,
53 awaiting review). Random seed `3257324722672619128`, no rerolls:
Flexor carpi radialis, Sartorius, Pronator teres, Tensor fasciae latae.
Preserve authored and mirrored sides, with independent counterparts in standalone.

External run:
`E:/development/WIP_models/muscle_reconstruction_workflow/runs/2026-10-21-standalone-four-muscle-transfer-afcbd2ec/`.
`run.json` hashes catalogue and target; `selection.json` stores all inventory rows,
selection seed, exact source builds, existing review limitations and native IDs.

Target is the previous `scp_migration_v001/serratus_skeleton_native_v001.anthroforge`
under the October 13 serratus run. Keep source skeleton unchanged; output a separate
versioned project under this new run. Do not reuse addon triangle indices on new SCP
topology: capture against explicitly corresponding target surfaces and compare actual
positions, full paths, base surfaces, inflation and cropped/two-sided output.

Next: extract source RNA, current Free paths, structural bindings, loft correspondence,
inflation settings and meshes; inspect source geometry; reconstruct through native app
contracts. Qualify source/mirror shapes, persistence, edit propagation and undo. Record
any observed app defects at their owning boundary before changing production code.
Maintain computational history for algorithm changes and the reconstruction skill for
verified lessons. Source approval remains separate from migration acceptance.

Observed gap: addon explicit material stations were absent at the standalone surface
boundary. Arclength reassignment increased FCR from 325 to 6494 vertices and changed
TFL inflation by 0.315 scene units. Optional, identity-qualified material correspondence
now belongs to SurfaceAlignment; native sampling maps authored parameters to stations.
`surface.correspondence` uses normal policies/jobs; Realign explicitly resets it.
Resolution 3 preserves donor grids without adding refinement (the donor has more rows).
All four source-side inflation outputs match within 6.4e-7 scene units with identical
vertex counts. This establishes shape parity, not final migration acceptance yet.
26 focused tests and five native CTests pass. Complete gate/portable/UI checks pending.
One-off scripts: `tmp/extract.py`, `tmp/transfer.py`, `tmp/compare.py`; captures and
baseline/current comparisons are in the external run. `muscles_trial_v001.anthroforge`
is an intermediate only. Mirror capture/build and lifecycle qualification remain active.


Checkpoint: bilateral output has 8 editable tissues, 8 membranes and 22 Fibers.
All eight inflation surfaces match within 6.4e-7 scene units. Bone edits (SCP13,
SCP12 and its mirror), eight inflation edits and eight Fiber edits propagate; all
undos restore geometry. Final copy `skeleton_four_muscles_v001.anthroforge` saved
revision 2001; startup reaches 2314 without shape changes (max 1.34e-13).
Original Blender and standalone skeleton SHA-256 hashes remain unchanged.
`qualification.json`, `comparison.json`, `views/` and `muscle_inventory.html` hold
actual evidence. Background D3D11 viewport capture is valid with no warnings;
source/native comparisons have been visually inspected. No interactive claim.
Full Windows gate: 1653 tests and five native CTests pass, native/script style and
mypy pass. Additional correspondence/branch/history/source checks: 20 pass.
Portable packaging/qualification and attachment proximity audit remain in progress.
