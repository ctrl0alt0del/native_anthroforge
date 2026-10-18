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

Research and addon/application inspection underway; no implementation yet.
Standalone starts at 0.1.5. Preserve the unrelated untracked root `__init__.py`.

## Verification

Read-only source inspection so far. Development, behavioral, GUI, profiler, and
portable validation remain to be run after implementation.

## Next actions and blockers

1. Finish tracing source detector/runtime/UI integration and standalone lifecycle.
2. Implement the shared issue contracts and providers with behavioral tests.
3. Integrate desktop UI, qualify packaged behavior and responsiveness, document,
   then merge/push only after required checks pass.

## Recovery inputs

Addon reference checkout: `C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
Standalone: `E:/development/anthroforge`; normal setup in `docs/development.md`.
Qt reference: https://doc.qt.io/qt-6/model-view-programming.html
