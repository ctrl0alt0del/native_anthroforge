# Standalone issue reporting

- Task branch: `codex/issue-reporting`
- Integration branch: `main`
- Starting revision: `c5facaa3e13ab615a9b2026b7101cd809057b46d`
- Status: pending release qualification
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
Desktop Issues UI and actual navigation/filter/dismissal/repair checks pass; screenshots
were visually inspected. Activity shares the keyed-record model and its GUI acceptance
passes. Failed detector scopes are isolated; queued cancellation, late old callbacks,
scope retirement, undo/redo and desktop/headless Open reset were hardened. Headless
save(wait) now drains only document writers, preserving read-only diagnostics semantics.
Release versions are updated to 0.1.6. Preserve untracked root `__init__.py`.
Final lifecycle review added cancellation/retry coverage: cancellation retains the original
failure as retryable evidence, and successful synchronous task rechecks complete repair
verification immediately. Malformed duplicate detector identities are isolated per scope.
A subprocess exercises issue detection/repair with no Qt or Blender imports.

## Verification

The full development gate passed 510 tests (seven existing Qt deprecation warnings),
native/style/type checks and native runtime/numerics loading. The final lifecycle
changes above passed 15 targeted tests; rerun the full gate before packaging.
`tools/activity_acceptance.py` and `tools/issues_acceptance.py` passed actual GUI checks;
captures under `build/issues-016/gui` were inspected. Full development and portable
gates remain pending; this checkpoint is not merge-ready.

`tools/issues_profile_acceptance.py` passed eight serial normal/snapped drag recordings
with Issues closed/open/open/closed, F12 toggling within each gesture, confirmation and
undo. All reports complete; no issue-model resets or changes during captured drags.
Input dispatch means were 6.34–6.68 ms normal and 6.79–7.19 ms snapped across the
open/closed trials. These are inclusive recorded timings, not an unprofiled speed or
zero-overhead claim. Compact hashes/metrics: [evidence](issue-reporting-evidence.json).
The initial unqualified trial let its fixed pixel path leave the cube when opening
the panel shrank the viewport. Fixed projection preserves 300 pixels/metre across
variants; the failed fixture run is excluded, not counted as success.

## Next actions and blockers

1. Run the complete development gate and final lifecycle/model tests.
2. Build/qualify 0.1.6 portable distribution, including issues JSON workflow and
   actual packaged Issues panel; inspect its screenshot and create source archive.
3. Review ownership/coupling and document final evidence,
   then merge/push only after required checks pass.

## Recovery inputs

Addon reference checkout: `C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
Standalone: `E:/development/anthroforge`; normal setup in `docs/development.md`.
Qt reference: https://doc.qt.io/qt-6/model-view-programming.html
