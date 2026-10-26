# Skin migration 0.4.0

- Task branch: `codex/skin-040`; integration: `main`.
- Starting revision: `6260864` (qualified 0.3.7 UI workbench).
- Status: source inventory complete; release scope/UI/export questions pending.
- Last updated: 2026-10-26, Europe/Bucharest.
- Direct work, no subagents. All execution/validation must remain background/hidden.

## Outcome and acceptance

User requests moving existing addon skin functionality into the standalone app for
0.4.0. Preserve anatomy, geometry/attachment behavior and the existing engineering,
checkpoint/push and single-distribution rules. No runtime changes are made yet.

## Decisions and relevant files

- [Migration inventory](../skin_040_inventory.md) records production code owners,
  settings, current-versus-legacy behavior, numerical porting work and future evidence.
- Addon source `fae36aba1b208676cf21d7c4a78a20d5b1f68c66`; inspected skin paths clean.
- Standalone skin-only export scope is already confirmed. Format is not.
- Reuse the coordinator, native geometry/material contracts, brushes, Issues, profiler,
  immutable results and workbench; no Blender runtime or duplicate scheduling system.
- Current addon publishes usable quality-warning geometry. Older hard-rejection prose
  is superseded by actual `core/mesh_issues.py` and its callers.

## Current state and verification

Read panels/operators, model/settings, field/gap kernels, topology/guide preparation,
reference/LE/FAST/contact code, publication and existing fixture names. Checked official
upstream APIs. No runtime/parity/GUI qualification or geometry acceptance performed.
App version/schema and all production files remain unchanged. Unrelated root
`__init__.py` is preserved. Source `.blend` files remain untouched.

## Pending decisions and next actions

1. Full current skin workflow versus generation/topology first.
2. OBJ-only export, OBJ+glTF, or defer export.
3. Dedicated Skin mode with one Build Skin action versus document-root inspector.

Questions were sent asynchronously. Do not assume unanswered choices are approved.
After responses, settle remaining material behavior (especially construction versus
update invalidation, guide roles and shared-consumer capture), consolidate specification
and plan, then execute integrated increments. Inventory is not an approved release spec.

Keep legacy addon warm-reference migration and rig/armature baking distinct from new
standalone skin. No automatic remeshing on deformation and no silent backend fallback.

## Recovery inputs

Addon root is recorded in the inventory. Windows-only fixtures remain under
`E:/development/WIP_models`; local presence is not proof of geometry acceptance.
The containing Git commit identifies this checkpoint; inspect remote reachability
before resuming from another machine.
