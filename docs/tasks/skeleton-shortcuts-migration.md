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
than claiming migration from successful API calls alone. No checks passed yet.
