# Skin migration 0.4.0

- Task branch: `codex/skin-040`; integration: `main`.
- Starting revision: `6260864` (qualified 0.3.7 UI workbench).
- Status: release scope/UI/export confirmed; expanded source inventory complete;
  detailed specification and implementation plan next. No runtime implementation yet.
- Last updated: 2026-10-26, Europe/Bucharest.
- Direct work, no subagents. All execution/validation must remain background/hidden.

## Outcome and acceptance

User requests moving existing addon skin functionality into the standalone app for
0.4.0, including calculating fitted bones/weights to reproduce shortcuts. Preserve
anatomy, geometry/attachment behavior and the existing engineering,
checkpoint/push and single-distribution rules. No runtime changes are made yet.

## Decisions and relevant files

- [Migration inventory](../skin_040_inventory.md) records production code owners,
  settings, current-versus-legacy behavior, numerical porting work and future evidence.
- Addon source `fae36aba1b208676cf21d7c4a78a20d5b1f68c66`; inspected skin paths clean.
- Full current skin pipeline plus shortcut-to-bone fitting is in scope.
- Confirmed delivery priority: reproduce existing addon behavior first, then improve it
  in later work. Preserve algorithms/defaults/supported cases while adapting ownership
  to the standalone architecture; keep proposed enhancements separate from migration.
- Export starts with OBJ, preserving quads; keep a narrow, extensible format interface.
  OBJ does not serialize rigs. Retain fitted data/preview in the project.
- Add Skin to the existing right inspector and arrange Shape / Shortcuts / Inspect /
  Skin vertically on its left edge. This replaces the proposed separate Skin mode.
- Reuse the coordinator, native geometry/material contracts, brushes, Issues, profiler,
  immutable results and workbench; no Blender runtime or duplicate scheduling system.
- Current addon publishes usable quality-warning geometry. Older hard-rejection prose
  is superseded by actual `core/mesh_issues.py` and its callers.
- Bone fitting is untracked local addon work; its source fingerprints and actual public
  versus authoring-only contracts are recorded in the inventory. Do not attribute it to
  the clean source commit or claim existing qualification of its standalone port.

## Current state and verification

Read panels/operators, model/settings, field/gap kernels, topology/guide preparation,
reference/LE/FAST/contact code, bone sampling/fitting/preview/publication and existing
fixture/test names. Checked official
upstream APIs. No runtime/parity/GUI qualification or geometry acceptance performed.
App version/schema and all production files remain unchanged. Unrelated root
`__init__.py` is preserved. Source `.blend` files remain untouched.

## Next actions

1. Consolidate specification and plan with the full fitting workflow and vertical tabs.
2. State construction/update invalidation, guide roles, shared-consumer capture and
   project compatibility explicitly. Use the addon's behavior where applicable.
3. Qualify paired fixtures and dependencies before integrated native/runtime delivery.

All three initial questions are answered. No automatic minimal-bone search or
multi-shortcut rig composition is implied: preserve the existing configurable bone
budget and independent fits. General animation editing and rig-capable export remain
separate. No automatic remeshing on deformation and no silent backend fallback.

## Recovery inputs

Addon root is recorded in the inventory. Windows-only fixtures remain under
`E:/development/WIP_models`; local presence is not proof of geometry acceptance.
The containing Git commit identifies this checkpoint; inspect remote reachability
before resuming from another machine.
