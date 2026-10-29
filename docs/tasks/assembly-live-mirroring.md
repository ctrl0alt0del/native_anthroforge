# Migrated assembly: live SCP and VCP mirroring

- Branch: `codex/assembly-live-mirroring`; integration: `main`.
- Baseline: `395b5b8b`; writer: local direct work.
- Status: addon policy inspected and shared-target inspection corrected; full-assembly
  requalification and canonical package checks in progress. Original project untouched.

## Authorized outcome

Convert the migrated skeleton/96-muscle assembly to live mirroring for SCPs and
TissueVCPs. Replace the 26 independent opposite-side bones with reflected instances,
add reflected muscles, preserve source geometry and remap retained relationships.
Deliver a new self-contained project copy; preserve the original file. No new
geometry algorithms or silent rebinding. Keep tools/tests background-only.

Source: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
Expected source SHA256: `308c216c85d9458d83e163bc3ed2ab85338bccd3adeb496981ffe35ec8275dac`.

## Investigation and validation

Inspect source/counterpart identities, construction sharing, external consumers,
mirror plane, midline supports, driver ownership and geometry correspondence before
rewriting references. Reuse the existing reflection/provider/material contracts.
Check reopen, visible bilateral geometry, no duplicate authored opposite-side
objects, retained bindings, and representative shortcut updates. Inspect hidden
rendered results and report any intentional differences from independent sources.

Official reference consulted: [Blender 5.0 Mirror modifier](https://docs.blender.org/manual/en/5.0/modeling/modifiers/generate/mirror.html).
The application's confirmed strict-reflection contract remains authoritative.

## Recovery

Read `docs/specification_035.md`, `docs/mirroring_035.md` and relevant migration
inventories. Initial package has 59 SCPs, 96 tissues, no mirror rules. Unrelated
root `__init__.py` remains untouched. Resume from the findings below; do not redo
the completed inventory or infer consent from elapsed time.

## Candidate and evidence

`tools/assembly_mirror_migration.py` reads the fixed source, verifies no surviving
typed references cross into the 43 removed records (26 bones, 14 controls, 3 curves),
and writes `build/assembly-live-mirroring/candidate.anthroforge`. One Y=0 scoped rule
is anchored to Spine for editable controls; central bones opt out, with bilateral
boundaries retaining that same rule. No new authored hierarchy nodes are introduced.
There are 563 live instances: 27 SCPs (one empty Hook group), 96 TissueVCPs,
96 Membranes, 326 Fibers, 3 ordinary curves and 15 controls. No plane conflicts.

25/26 old opposite bones match reflected source geometry within numerical noise.
Scapula differs by maximum sampled distance 0.026545 m, RMS 0.003688 m in the source's
canonical scale; its prior independently evaluated Shrinkwrap shape was asymmetric.
The live counterpart intentionally becomes exact source reflection. No source shape changed.

`tools/qualify_assembly_mirrors.py` verifies reopened source geometry/bindings, then
Humerus Length 3.1134088, Radius Length 2.5114212, Thumb Metacarpal Thickness 0.0735000
and Ribs Top Radius 3 against the original file. All source-side geometry and binding
comparisons pass, with no task errors. Original SHA256 remains unchanged.
Single trials: original/mirrored Humerus 2.77/4.41 s, Radius 2.20/3.69 s, Thumb .74/2.21 s,
Ribs 5.31/8.43 s. These include extra mirror diagnostics; no performance improvement claimed.
Tool lint/format and two architecture checks pass.

Hidden front/oblique captures show the complete bilateral assembly and were viewed.
They contain 3,711,840 render vertices and no QML warnings. First captures were blank
because source Qt loaded build/dev while Python loaded the qualified native DLL;
those invalid captures were replaced after aligning both runtime paths. Override
desktop.runtime.build_directory and desktop.offscreen.build_directory to the same
`AF_NATIVE_BUILD` when reproducing; import application.session before desktop.capture.
No interactive desktop input or visible windows were used.

## Resolved shared-target behavior

User response: “How it's done in addon? do the same”. Inspected addon
`vcp_mirror_runtime._copy_fiber_instance/_copy_mirror_transform`, `fiber_instance_runtime.update`
and `scp_runtime/mirror_scene.py`. Bone-attached fibers and SCPs reflect evaluated source
geometry without a second capture. Later muscle-backed independent evaluation is outside
the standalone's confirmed strict-reflection contract and is not copied.

The app compared reflected source anchors with the original-side anchor on a shared bone,
producing 182 false mismatches. Shared inspection now reports `binding_mode=source_reflection`
and `surface_contact=not_checked`; no rebinding or geometry mutation. Counterpart/plane checks
remain for non-shared relationships. Shared supports can still be asymmetric; this is not
a surface-contact guarantee. The previous proposal to capture new anchors was withdrawn.
19 focused tests pass, covering source geometry, shared binding persistence/plane edits,
missing counterparts and ownership/style limits. Regenerated candidate has 689 mapped
relationships and no false mismatch rows. All four full-assembly shortcut trials pass again with exact source geometry/bindings and
no task errors. Gate first stopped on a missing Python return-value parameter type; a
signature-only annotation fixed that, with no runtime behavior change. Full gate rerun pending.

Canonical 0.4.2 executable built from clean runtime checkpoint `b3d6f898`; subsequent source
change is a type annotation only. Relocated mirror/Issues and full-assembly checks are running.
No visible window or desktop input. Development gate is running native style/full tests.

Delivery copied, with matching candidate/delivery SHA256:
`86c08109700bb6e12de807dca8ef93ba37efe33f0a60dc3c2a87a71cc87be554`.
Path: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_live_mirroring_v001.anthroforge`.
Original source SHA remains unchanged. Deliverable is 264.9 MiB, schema 9.

Ownership review: correction stays in the shared application inspection policy; geometry,
retained material bindings and Core serialization are untouched. Migration reuses scoped rules,
typed reference inspection, selective resource saving and source provider reflection. No new
mirror worker, graph duplication, numerical approximation or opposite-side driver chains.

Next: finish gate/relocated checks, inspect packaged captures, update source archive and merge.
