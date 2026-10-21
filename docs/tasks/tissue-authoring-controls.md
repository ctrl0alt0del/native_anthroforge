# Tissue authoring controls

- Task branch: `codex/tissue-authoring-controls`
- Integration branch: `main`
- Starting revision: `4c4b7bb06d7636eb8af9ff8c454f0fa555f93323`
- Status: implementation and qualification complete; ready for normal merge
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
- User confirmed Overall depth: type/drag maximum depth and scale all four stations.
- Copy side settings includes inflation/profile/control and height smoothing settings.
- Other audit findings are outside this task; do not restore retired addon workflows.

## Current state

Boundary Power, copy-side controls and stacking group/discovery allowance are implemented.
Group and allowance participate in dispatch read validation and targeted plan invalidation;
changes reuse intrinsic geometry. Explicit pairs may override group suppression as in the
addon. Shared copy-side operation copies inflation and smoothing, preserves inactive parts,
and uses existing capability/topology checks. Native profile scaling and Overall depth are
implemented, preserving ratios through zero within one drag. A committed all-zero profile
needs a station edit/reset before proportional scaling. Preview uses the same adapter.
Qt command input/output boundaries now snapshot projected records and convert tuple arrays
to QML lists; actual profile dragging exposed these transport gaps. Unrelated root
`__init__.py` preserved.

## Verification

The full development gate passes 1,534 tests, five native contracts, lint/format, typing,
native/script function limits and numerical/runtime checks. The expanded focused authoring,
profile and native stacking subset passes 34 tests.
Actual offscreen QML checks pass all four controls, numeric type/drag, side copy, undo/cancel,
profile drag through zero, preview isolation and cancellation. Inspector captures inspected.
Hidden native rendering also passes: stacked/independent groups, proportional raised profiles,
copied envelopes and hover/click agreement. Actual captures inspected. The source CLI passes
the new portable authoring batch and round trip. Its first draft attempted to enable the
second side on an attachment-locked example; the shared policy correctly rejected it, so
portable coverage copies inactive side settings and the independent GUI fixture covers
envelope creation. The canonical 0.2.3 package is built from `2287808` with clean tracked
source. The full relocated minimal-PATH portable suite passes, including the new authoring
operations and saved parameters. No interactive desktop acceptance is claimed.
Initial test fixture incorrectly used a smoothing `enabled` field; corrected to radius.

## Ownership review

Coordinator review, separately from tests: core records own group/allowance validation;
application policies own copying, topology guards, group mapping and plan read signatures;
the existing native stacker owns eligibility/search and the native parameter adapter owns
depth scaling. QML owns only gesture baseline and presentation. Command transport snapshots
owned values at the desktop boundary. No second scheduler, numerical Python fallback,
per-feature undo mechanism or new geometry cache was introduced. No blocker found.

## Next actions and blockers

Refresh packaged documentation and the single source archive, push this completion record,
then merge/push normally into `main`. Runtime build identity remains `2287808`; subsequent
changes are documentation only. Git ancestry records final integration.

## Recovery inputs

Normal Windows setup; no production source scene is required. Keep validation background-only.
Local generated evidence belongs under `build/tissue-authoring-controls*`.
