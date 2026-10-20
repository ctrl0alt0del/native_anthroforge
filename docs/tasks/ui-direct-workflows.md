# Direct UI workflows and report review

- Task branch: `codex/ui-direct-workflows`
- Integration branch: `main`
- Starting revision: `bad422f0193f2f871f05e16a0815da2377f76eb4`
- Status: in progress
- Updated: 2026-10-20, Europe/Bucharest
- Writer: local desktop chat; direct work, background validation only

## Confirmed scope

Implement the reviewed simplifications using shared application policies and coherent
undo: direct stacking settings, direct closed-loft creation with Realign, source editing,
Hook member selection, image tracing, nonmodal workspace presentation and inline naming,
direct report text editing, and discoverable Tissue creation.

User decisions:
- Fiber creation is available without curve edit mode and defaults to nearest SCP
  bindings. Explicit optional target/role/interior-point overrides remain available.
- Delete confirms only when other objects are affected; all entry points share policy.
- Choosing a tissue weight field enters editing; committing a weight applies to selected
  points in one undo action.
- Focus immediately creates a workspace for selected anatomy and descendants with an
  automatic name. Rename and membership options remain available afterward.
- Closed lofts create immediately in one undo action; Realign remains available.

Keep optional inflation previews, coherent region/gesture drafts, explicit anatomical
conversion, save-revision choices and permanent report-file deletion confirmation.
No geometry algorithm substitutions, source mutation on inspection or dummy SCPs.

## Reports

Three inbox reports inspected read-only, all from 0.2.1:
- `16203ca77e2744b9b2dbfc4fa2eae8dd`: excessive ellipsis.
- `22301967f3f5478595777eb751c93263`: Anatomy/Construction should be tabs.
- `2f4815be5165470680437e032b2c0966`: misaligned icons.

Compare annotated captures with current shared controls before changing behavior.
Preserve original report archives. Resolve still-reproducible defects in this task.

## Ownership and acceptance

Shared commands/policies own nearest binding, deletion impacts and validation. Desktop
adapters own navigation and selection; QML dispatches explicit user edits, never writes
on initialization/refresh. Reuse native nearest queries, coordinator and transactions.
Validate API policies, single undo, rejected edits, selection, dense lists and offscreen
QML. Inspect captures at representative DPI/layout sizes, run the development gate,
qualify the single canonical 0.2.2 package and source archive, then merge/push.

## Current state and next steps

First implementation checkpoint (not release-ready):
- Native nearest-SCP pin capture inside the existing Fiber creation job, with optional
  explicit overrides and dispatch-time provenance. No Python geometry loop.
- Shared deletion-impact query, direct closed surface creation/Realign, source/member
  navigation, tracing, weight editing, workspace focus/presentation and direct report text.
- Direct stacking controls and toolbar/menu Tissue creation with searchable source chooser.
- Fiber options use a virtualized point list rather than one target control per point.
- 24 focused core/architecture tests pass; mypy and Ruff pass; the existing offscreen
  tissue creation check passes. Full new interaction coverage, report DPI verification,
  documentation, development gate and packaging remain incomplete.

Prior ignored audit probe reproduced unapplied stacking checkbox changes, hidden Fiber
creation, per-point selector clutter, source navigation without editing and Hook member
selection doing nothing outside edit mode.

1. Finish interaction regression checks, including dense bindings, rejected settings,
   direct report text, conditional deletion, weights and nonmodal workspace navigation.
2. Compare current reports at representative DPI; fix any remaining layout defects.
3. Validate, package, update durable documentation, merge and push.

## Recovery

Use the normal repository Windows environment (`.venv`, native build). Evidence and
experiments under `build/ui-direct-workflows`; reports under the user's local
`AnthroForge/Reports`. Preserve unrelated untracked root `__init__.py`.
