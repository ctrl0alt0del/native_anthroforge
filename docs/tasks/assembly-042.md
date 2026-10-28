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

Foundation implemented: schema-8 provenance/reference records, explicit typed field adapters,
reference-aware validation/readiness and automatic Issues. Source inspection pins a package;
graph closure/selective resource transfer and coordinator-backed headless self-contained
construction import work with one-action undo. Existing primitive/deformer duplication now
uses the same typed remapper. Relationship-specific mapping and world-preserving parent
detachment work. Native full-content comparison rejects merely matching geometry counts;
explicit Fiber rebind uses existing current-shape capture. Missing references retain visible
invalid source results and surface evidence for later repair. Inherited mirror planes now use
explicit boundary scopes without dummy hierarchy nodes. Source/mirror mappings are distinct.
Reference repair works from retained package evidence after source deletion, through the same
mapping/binding policies and one-action undo. Desktop interaction, complete metadata provenance,
broader relationship/lifecycle coverage and production qualification remain unfinished; this
checkpoint is not a release.

Desktop import/repair entry points are now wired: File menu, searchable virtualized lists,
automatic preparation, stable footer, explicit rebind evidence, and Issues navigation.
Offscreen production dialog inspection found and corrected a collapsed list; the populated
625-record dialog now renders without QML warnings. No interactive acceptance is claimed.
Production skeleton copying initially caused unintended formula reevaluation and changed the
clavicle. Shared accepted-output adoption now distinguishes saved results from new edits;
SCM maps to the copied skeleton without a spurious rebind requirement. This needs broader
driver, lifecycle, result-provenance and shortcut-response qualification before release.

## Verification

Initial foundation checks pass. Current API/resource/architecture checks verify
selected resources, copied accepted definitions, source removal after inspection, persistence,
undo and cancellation. Mapping tests cover world-preserving parent changes, retained Fiber
bindings, missing supports, incompatible geometry, and explicit rebind. Focused mypy passes.
Current focused run: 25 assembly tests pass, plus desktop selection/undo/idle checks and
the two architecture checks. Repository mypy passes (562 source files).
Production smoke: 281 MB / 625-object source inspected in 2.79 s; SCM and required construction
prepared in 0.69 s, exposing five external relationships. This does not establish geometry parity.
Production/full-suite qualification remains pending. Baseline: 2,641 Python tests, six native suites and 32 portable checks qualified
by the preceding display/cache task. Keep new checks background/offscreen.

## Next actions and blockers

1. Complete graph closure, copy/resource adapters and headless import/mapping.
2. Complete lifecycle integration, reference repair and desktop workflow.
3. Qualify production geometry/lifecycle and rebuild the canonical package/source archive.

## Recovery inputs

Native: `C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native/bin/af_native.dll`.
Production: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
Artifacts belong under ignored `build/assembly-042`; do not alter production source files.
