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

Boundary Power, copy-side controls and stacking group/discovery allowance are implemented.
Group and allowance participate in dispatch read validation and targeted plan invalidation;
changes reuse intrinsic geometry. Explicit pairs may override group suppression as in the
addon. Shared copy-side operation copies inflation and smoothing, preserves inactive parts,
and uses existing capability/topology checks. Profile scaling remains pending implementation
and the user's UI choice. Unrelated root `__init__.py` preserved.

## Verification

23 focused authoring, stacking lifecycle/group and architecture tests pass. Initial tests
used a nonexistent smoothing `enabled` field; corrected to its supported radius setting.
Pending proportional profile tests, native discovery bounds evidence, actual offscreen QML
editing/visual inspection, development gate, and canonical portable-package qualification.

## Next actions and blockers

1. Trace stack grouping/allowance through dispatch, observation and persistence; add shared operations.
2. Add the four focused controls and tests; resolve profile interaction with the user.
3. Document computational intent; qualify, package, checkpoint/push and merge normally.

## Recovery inputs

Normal Windows setup; no production source scene is required. Keep validation background-only.
Local generated evidence belongs under `build/tissue-authoring-controls*`.
