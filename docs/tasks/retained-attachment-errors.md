# Retained attachments during skeletal edits

- Task branch: `codex/retained-attachment-errors`; integration: `main`.
- Starting revision: `5f64e153b387f5c5e41b550b12109efbe7dcdd2a`.
- Status: approved corrections in progress; material crop regression tests pass.
- Updated: 2026-10-23, Europe/Bucharest. Direct work; background-only validation.

## Outcome and acceptance

Investigate and fix the Humerus/Radius length and Thumb thickness attachment errors
in the migrated 96-muscle assembly. Establish the actual cause and explain the approach
to the user before changing attachment behavior. Preserve original project files,
retained binding intent, native numerical ownership and existing transaction semantics.

## Evidence and initial hypotheses

Migration qualification reproduced the same errors in both the original assembly and
the migrated copy. Humerus/Radius edits were +5%; the old Thumb helper added 0.05
to 0.07 (about +71%, incorrectly reported as +5%). A fresh actual +5% Thumb edit
reproduces the same seven failures; historical raw evidence is preserved. Humerus/Radius edits report missing tissue
material locations on FDS radial Fibers. Thumb thickness reports union-covered locations
on seven Fibers. Those error messages identify rejection sites, not proven physical loss
of a valid anchor. Diagnose active versus unused field influences, correspondence,
surface topology/provenance and dispatch/publication revisions before choosing a repair.

Native rejection sites: `material_binding_query.cpp`, `material_binding_frames.cpp`,
`triangle_material_frames.cpp`. Existing exterior placement policy qualifies new capture;
retained bindings must not silently choose a new nearest point during deformation.

## Recovery inputs

- Final copy: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
- Original copy, mappings and paired failures: same folder's `input.anthroforge`,
  `compact-mapping.json`, `failure-15.json`, `failure-16.json`, `failure-21.json`.
- Existing reproducer: `tools/probe_skeleton_control_failures.py`.
- Local diagnostic output: `build/retained-attachment-errors/` (ignored).
- Preserve unrelated root `__init__.py`; no desktop input or visible windows.

## Next actions

1. Reproduce with per-binding/field diagnostics and isolate the rejected material query.
2. Compare reference/current geometry and material provenance; test discriminating cases.
3. Explain an evidence-backed correction before behavior changes; ask if product semantics
   genuinely require a choice. Then implement, qualify real geometry/undo/persistence,
   update computation history, package, and merge through the established workflow.

## Confirmed causes and approved correction

The FDS crop plane cuts away active attached material during Humerus/Radius changes.
Its base topology is unchanged. A failed endpoint changes signed distance from
+0.060001 to -0.081851. Using the original accepted crop base with the new inflated
rest resolves all 188 Humerus and 468 Radius failed material records without rebinding.
The user approved preserving the material cut; explicit crop edits define a new cut.
Accepted material state now retains `crop_base`; resource ownership and serialization
follow existing accepted-state contracts. Older accepted states use their own base.

Thumb source triangle rows are unchanged (all 708). Thickening actually buries the
proximal patches under the metacarpal. With an actual +5% edit, their signed exterior
distances change from positive to negative. The user approved following the same
object's exterior while retaining the original reference, including restoration.
Native Boolean provenance will retain the untrimmed construction coordinates. Missing
material is projected to that union's exterior in construction coordinates and then
transported through the displayed triangle's deformation. Stored bindings stay intact;
no other object is eligible. Post-construction deformation must preserve this chart.

Evidence is in `build/retained-attachment-errors/`: `frozen-material-crop.json`,
`thumb-five-percent-coverage.json`, `true-five-percent-{15,16,21}.json`, and the
per-record diagnosis directories. `tools/diagnose_retained_attachments.py` is the
maintained read-only reproducer. Fourteen crop/material regression tests pass.
Native exterior following, actual-project qualification, visual inspection, full gate,
packaging and merge remain unfinished.

## Implementation checkpoint

Native exterior following is implemented with a persistent untrimmed construction
chart, layer-isolated spatial queries, and unchanged binding records. First combined
gate: 1,980 tests/five CTests pass, including native function limits. Real first edits
all complete without the original attachment errors. During history validation, the
profiler revealed a separate discarded Ulna pose job: formula invalidation cancelled
it while queued, then an unchanged formula result did not replace it. This is now
reproduced by `test_pose_formula_refresh.py` and corrected through the existing
renewable-job/restart contracts. Humerus edit/reverse now restores tissue vertices
within 1.8e-12, including through save/reopen; pending final combined verification,
shape inspection and canonical packaging.
