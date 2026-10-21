# Tissue authoring controls

- Task branch: `codex/tissue-authoring-controls`
- Integration branch: `main`
- Starting revision: `4c4b7bb06d7636eb8af9ff8c454f0fa555f93323`
- Status: in progress
- Last updated: 2026-10-21, Europe/Bucharest
- Active writer: current desktop chat, direct work

## Outcome and acceptance

Implement only the four addon gaps selected by the user: Boundary Power in the
inspector, explicit stacking families and discovery displacement allowance, copying
inflation side settings (selected/all parts), and proportional Section Profile scaling.
Keep desktop/headless validation and undo shared; retain native numerical ownership,
Manual provenance, stable editing layouts and existing topology/relationship rules.

## Decisions and relevant files

- No new release version requested: deliver the canonical 0.2.3 package and source archive.
- Reuse tissue operations, stack settings, shared numeric controls and existing coordinator.
- Stack family means explicit suppression of within-family pairs, separate from atomic
  dependency evaluation groups. Default empty family keeps independent tissues separate.
- Existing addon discovery allowance defaults to 0.5; this is not a displacement clamp.
- Profile scaling interaction is pending the user's answer (maximum depth versus factor).
- Copy side settings includes inflation/profile/control and height smoothing settings.
- Other audit findings are outside this task; do not restore retired addon workflows.

## Current state

Read current specification, engineering guidelines, addon side tools and standalone
evaluation boundaries. No implementation edits yet. Unrelated root `__init__.py` preserved.

## Verification

Pending shared-operation/lifecycle tests, native checks, actual offscreen QML editing and
visual inspection, development gate, and canonical portable-package qualification.

## Next actions and blockers

1. Trace stack grouping/allowance through dispatch, observation and persistence; add shared operations.
2. Add the four focused controls and tests; resolve profile interaction with the user.
3. Document computational intent; qualify, package, checkpoint/push and merge normally.

## Recovery inputs

Normal Windows setup; no production source scene is required. Keep validation background-only.
Local generated evidence belongs under `build/tissue-authoring-controls*`.
