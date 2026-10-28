# Cross-project anatomy assembly — 0.4.2

- Task branch: `codex/assembly-042`
- Integration branch: `main`
- Starting revision: `de1f475`
- Status: in progress
- Last updated: 2026-10-28, Europe/Bucharest
- Active writer: local Codex

## Outcome and acceptance

Implement the confirmed [assembly contract](../assembly_042.md), with desktop and
headless import, typed graph copies, explicit external mapping, schema 8, repairable
unresolved references, provenance, and production/portable qualification. Keep 0.4.2.
Preserve numerical algorithms, source files and unrelated root `__init__.py`.

## Decisions and relevant files

- Independent copies; source world placement; optional attached tissues.
- Resolve placement parents/follow targets before import. Other references may remain
  unresolved. Explicit rebind for incompatible material coordinates.
- Preserve inherited mirror rules at boundaries. External driver outputs remain disabled
  until explicitly mapped and enabled. Exclude project-wide skin/workspaces/history.
- Shared application operations, one coordinator, native numerical work, 15-line functions.
- Search reference: [OpenUSD relationship remapping](https://openusd.org/release/user_guides/namespace_editing.html).
  Use explicit typed references; no USD dependency or live composition is introduced.

## Current state

Initial foundation implemented: schema-8 provenance/reference records, explicit typed field
adapters, reference-aware registry validation, local missing-input errors and an automatic
Issues provider. External declarations are not scene objects. No import command/UI yet.

## Verification

Initial 13 foundation/architecture/resource tests pass; focused Ruff/mypy pass. Full
qualification pending. Baseline: 2,641 Python tests, six native suites and 32 portable checks qualified
by the preceding display/cache task. Keep new checks background/offscreen.

## Next actions and blockers

1. Complete graph closure, copy/resource adapters and headless import/mapping.
2. Complete lifecycle integration, reference repair and desktop workflow.
3. Qualify production geometry/lifecycle and rebuild the canonical package/source archive.

## Recovery inputs

Native: `C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native/bin/af_native.dll`.
Production: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
Artifacts belong under ignored `build/assembly-042`; do not alter production source files.
