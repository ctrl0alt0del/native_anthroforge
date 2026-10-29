# Migrated assembly: live SCP and VCP mirroring

- Branch: `codex/assembly-live-mirroring`; integration: `main`.
- Baseline: `395b5b8b`; writer: local direct work.
- Status: inspection in progress; no source project changes.

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
root `__init__.py` remains untouched. Next: inventory all relationships and build a
reproducible migration/qualification script before saving the new candidate.
