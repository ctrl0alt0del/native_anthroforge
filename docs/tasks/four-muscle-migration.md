# Four random addon muscles on the migrated skeleton

- Branch: `codex/four-muscle-migration`; integration: `main`.
- Base: `a8022a4`; status: inventory complete, extraction in progress.
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
