# Standalone issue reporting

- Task branch: `codex/issue-reporting`
- Integration branch: `main`
- Starting revision: `c5facaa3e13ab615a9b2026b7101cd809057b46d`
- Status: in progress
- Last updated: 2026-10-18, Europe/Bucharest
- Active writer: desktop chat, direct implementation

## Outcome and acceptance

Inspect the Blender addon's issue system and migrate its responsibility boundaries
into the standalone application before the other proposed 0.1.6 improvements.
Deliver shared headless/desktop reporting, current-system detectors, filtering,
navigation, dismissal, explicit recovery, and honest check/freshness state.
Preserve scheduling, transactions, undo/checkpoints, workspaces, and profiling.

## Decisions and relevant files

- Source reference: addon `core/issues/{model,repository,reporting,listening,
  presentation,resolution,system}.py`, domain adapters and warning UI/runtime.
- The addon separates producer-scoped reporting, detection, presentation, and
  explicit resolution. Older check completion cannot replace newer evidence;
  failed checks retain previous evidence; fixes require fresh verification.
- Reuse the standalone task coordinator, native algorithm boundary, incremental
  desktop models, and explicit application commands. No Blender runtime dependency.
- Follow [engineering guidelines](../engineering_guidelines.md) and
  [continuity](../work_continuity.md). No agents or Jira workflow.

## Current state

Addon responsibility tracing is complete. First implementation adds immutable
issue evidence, provider/scope reconciliation, generation/epoch checks, discovery,
registered explicit repairs with verification, shared issue API, and read-only
coordinator jobs. Initial providers cover current SCP/control evaluation,
unavailable attachment surfaces, dependency-blocked outputs, and task failures.
Desktop Issues UI is wired with incremental rows; GUI qualification is still pending.
Activity now shares the keyed-record model implementation; its behavioral tests pass.
Standalone starts at 0.1.5. Preserve the unrelated untracked root `__init__.py`.

## Verification

Ruff and mypy passed. 20 focused issue/core/incremental Activity tests passed at the
first UI checkpoint; the function-length gate identified three formatting-related
overlength functions, now refactored and awaiting rerun. Earlier construction and
interleaving run passed 29 behavioral tests. Full development, GUI, profiler, and
portable validation remain pending. This checkpoint is not merge-ready.

## Next actions and blockers

1. Finish detector failure isolation, target retirement, repair cancellation and
   stale/publication coverage; inspect actual Issues UI and preserve drag performance.
2. Run focused/full gates and expand GUI/profile acceptance.
3. Qualify packaged behavior and responsiveness, document,
   then merge/push only after required checks pass.

## Recovery inputs

Addon reference checkout: `C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
Standalone: `E:/development/anthroforge`; normal setup in `docs/development.md`.
Qt reference: https://doc.qt.io/qt-6/model-view-programming.html
