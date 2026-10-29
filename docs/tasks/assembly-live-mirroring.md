# Migrated assembly: live SCP and VCP mirroring

- Branch: `codex/assembly-live-mirroring`; integration: `main`.
- Baseline: `395b5b8b`; writer: local direct work.
- Status: candidate and independent qualification complete; awaiting the user's
  midline-anchor policy answer. No production-code or source-project changes.

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

## Pending user decision — do not silently change attachment policy

The current SharedMirrorTarget keeps only (source, binding), and mirror validation
resolves that original-side binding on the same midline target. All 182 shared
relationships therefore report mismatch. This does not mean 182 actual surface gaps:
the check compares reflected positions with original-side material coordinates.
Confirmed exterior-placement probes show source/reflected surface distances broadly
similar, with genuine existing asymmetry on central geometry; no points were rebound.

The async question asks whether to add an explicit opposite-side material anchor
on the same bone for validation, retaining exact reflected geometry and reporting
real drift, or keep current sharing and its warnings. No answer has arrived yet.
The user previously requested discussion before changing attachment behavior.
Keep this branch unmerged and the candidate under build until that choice is resolved.
If approved, implement through shared mirror binding/lifetime/persistence contracts,
validate actual gaps versus preserved offsets, qualify source updates and mirrored
diagnostics, then deliver a new project copy and any required canonical app update.
