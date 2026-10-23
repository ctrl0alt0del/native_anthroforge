# Retained attachments during skeletal edits

- Task branch: `codex/retained-attachment-errors`; integration: `main`.
- Starting revision: `5f64e153b387f5c5e41b550b12109efbe7dcdd2a`.
- Status: diagnosis; no attachment behavior changed.
- Updated: 2026-10-23, Europe/Bucharest. Direct work; background-only validation.

## Outcome and acceptance

Investigate and fix the Humerus/Radius length and Thumb thickness attachment errors
in the migrated 96-muscle assembly. Establish the actual cause and explain the approach
to the user before changing attachment behavior. Preserve original project files,
retained binding intent, native numerical ownership and existing transaction semantics.

## Evidence and initial hypotheses

Migration qualification reproduced the same errors with +5% property edits in both
the original assembly and the migrated copy. Humerus/Radius edits report missing tissue
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
