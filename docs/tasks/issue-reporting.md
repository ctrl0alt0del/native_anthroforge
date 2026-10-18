# Standalone issue reporting

- Task branch: `codex/issue-reporting`
- Integration branch: `main`
- Starting revision: `c5facaa3e13ab615a9b2026b7101cd809057b46d`
- Status: implementation and validation complete; ready for integration
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

Outage recovery on 2026-10-18: fetched origin and confirmed `069a05d` is pushed;
main remains at the starting revision. The complete 512-test gate and final GUI
evidence survived. Packaging stopped during C linking, with no build process left
running and the previous 0.1.5 executable still installed. Three documentation-only
edits survived locally and are checkpointed before restarting the cached package build.

## Verification

The final full development gate passed 512 tests (seven existing Qt deprecation warnings),
native/style/type checks and native runtime/numerics loading at `069a05d`.
The final lifecycle changes also passed 15 targeted tests. Actual Issues GUI acceptance
was rerun successfully at that revision, with no QML warnings; captures were inspected.
`tools/activity_acceptance.py` and `tools/issues_acceptance.py` passed actual GUI checks;
captures under `build/issues-016/gui` were inspected. Portable qualification also passed
after outage recovery, as recorded below.

`tools/issues_profile_acceptance.py` passed eight serial normal/snapped drag recordings
with Issues closed/open/open/closed, F12 toggling within each gesture, confirmation and
undo. All reports complete; no issue-model resets or changes during captured drags.
Input dispatch means were 6.34–6.68 ms normal and 6.79–7.19 ms snapped across the
open/closed trials. These are inclusive recorded timings, not an unprofiled speed or
zero-overhead claim. Compact hashes/metrics: [evidence](issue-reporting-evidence.json).
The initial unqualified trial let its fixed pixel path leave the cube when opening
the panel shrank the viewport. Fixed projection preserves 300 pixels/metre across
variants; the failed fixture run is excluded, not counted as success.

The resumed package build completed from clean tracked source at `7e98a91`, with
file/product version 0.1.6.0. A relocated distribution passed the complete portable
gate with minimal PATH and developer Python/Qt settings removed: imports, attachments,
primitives/deformers, deletion/subdivision, saving, inspection, rendering, GUI, runtime
profiling, and the issue detection/verified repair JSON workflow. The packaged Issues
capture was visually inspected. All 30 packaged QML files and three native DLLs match
the qualified inputs. Evidence is under `build/issues-016/portable` and the resumed
build log is `build/issues-016-package.log`; the interrupted log is retained separately.

## Delivery and integration

Application: `dist/AnthroForge.dist/AnthroForge.exe`.
Corresponding source archive: `dist/AnthroForge-0.1.6-source.zip`.
No product or validation work remains. Final integration is a normal merge/push into
`main`; Git ancestry records its completion. Preserve the task branch for recovery.

## Ownership and coupling review

Direct coordinator-authored review, separate from tests: the immutable issue model and
repository own evidence; reporting owns producer generation/epoch validation; listening
owns invalidation and registered detector dispatch; presentation owns read-only queries;
resolution owns explicit repair state and fresh verification. Domain adapters use existing
calculation commands and the one task coordinator. The desktop supplies labels, navigation
and keyed Qt rows, with no detector or geometry solver in drawing. Checks have no authored
document state, geometry outputs, undo entries or save barrier. Reset/close cancel old
checks and release captured documents through the existing job lifecycle. Numerical
geometry remains in C++; no Blender APIs, second worker pool, or persistent diagnostic
state was introduced. The shared RecordModel replaces duplicated Activity row mechanics.

## Recovery inputs

Addon reference checkout: `C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
Standalone: `E:/development/anthroforge`; normal setup in `docs/development.md`.
Qt reference: https://doc.qt.io/qt-6/model-view-programming.html
