# SCP workflow improvements, 0.1.7

- Task branch: `codex/scp-workflow-improvements`
- Integration branch: `main`
- Starting revision: `e8565e28328a205f10575f03928737ccd782d0d1`
- Status: complete; implementation, GUI, profiler and portable qualification passed
- Last updated: 2026-10-18, Europe/Bucharest
- Active writer: desktop chat, direct work

## Outcome and acceptance

Implement the original five recommendations postponed for issue reporting, recovered
from this chat's October 18 recommendation response:

1. Attachment/dependency inspector: what drives an SCP/control and what it drives,
   attachment surfaces/frames, topology-lock causes, related-object navigation.
2. Actionable issues: retain the shipped framework and distinguish actual cycle
   participants from downstream blocked outputs, with usable source relationships.
3. Workspace management/presentation: mixed SCP/control membership, rename/remove,
   independent category visibility and pickability, reusable presentation presets.
4. Display units: mm/cm/m for length display and entry; canonical geometry remains metres.
5. Shareable inspection report: desktop and CLI capture of one declared snapshot,
   explicit camera/selection, attachment/dependency data, authored/accepted revisions,
   geometry statistics, and an image in one archive.

Items 6–7 (measurement/bookmarks and new profiler metrics), project composition,
new anatomy systems and exact geometry collision diagnostics are outside this task.
Release as 0.1.7 because issue reporting has already shipped as 0.1.6.

## Ownership and contracts

Follow the engineering guidelines and confirmed recommendations D02/F05/G03,
G01–G03/C07, F04/F06/H04, A05, F10/H06. Extend shared application operations;
keep desktop adapters thin, numeric geometry in C++, presentation outside anatomy
undo, and inspection images/data from one frozen revision. Reuse the issue system,
task coordinator, native queries, render capture, storage and keyed Qt models.
Functions remain at most 15 physical lines. Preserve the legacy untracked `__init__.py`.

## Current state

Recovered the exact original numbered scope; inspected the shipped issue framework
and identified existing workspace, rendering and presentation boundaries. Main is
current with origin. Shared inspection API, precise cycle participants/causes,
mixed workspace membership and presentation/unit policies are implemented.
Desktop inspector, mixed workspace manager, category filters, unit-aware fields,
read-only background report archive and CLI are now integrated. The isolated Qt
renderer consumes a frozen temporary package and declared camera/selection; the
headless parent stays Qt-free. All five improvements, documentation and release
qualification are complete. See the final delivery evidence below.

## Verification

Baseline is 0.1.6 with 512 tests plus GUI/profiler/portable qualification. New behavior
requires focused API tests, actual GUI interactions and snapshot consistency checks,
the development gate, ownership review, and relocated portable qualification.

First checkpoint: 518 tests pass; strict mypy passes. Added native-anchor read-only
inspection, cycle/downstream distinction, 3,000-output graph, mixed workspace
round-trip and policy guard coverage. No GUI or release acceptance claimed yet.

Second checkpoint: actual GUI exercised millimetre entry (250 mm → 0.25 m),
workspace creation, geometry/curve visibility independence and picking exclusions.
GPU image+JSON export retained its revision during a concurrent rename. Captures
under ignored `build/workflow-017` were inspected; a workspace combo update-order
defect found visually was fixed. New export tests cover frozen geometry ownership,
failure/retry, cancellation, atomic destination preservation and Qt-free orchestration.
Full release gate, more interaction coverage and portable acceptance still pending.

Latest: the development gate passed 523 tests and all typing/style/native checks.
Expanded actual GUI checks cover hooks/cages, independent selection filters and
navigation into read-only context. Eight counterbalanced recorded drag trials passed;
see `scp-workflow-evidence.json` and `../development_status.md` for measured limits.
Version/docs are now 0.1.7. The next step is packaging the clean source checkpoint,
relocated portable checks (including the new report CLI), source archive and integration.

The user's existing `dist/AnthroForge.dist/AnthroForge.exe` is running. The first
package build was stopped before publication; preserve that process and directory.
Final build uses `AF_PACKAGE_OUTPUT=E:/development/anthroforge/dist/0.1.7`, producing
`dist/0.1.7/AnthroForge.dist`. All production changes are committed before rebuilding.

## Final delivery

The clean `190d387` build passed the full relocated portable gate under minimal PATH,
including the image/JSON report with no interpreter alias. Actual packaged viewport
and report images were inspected. The report contains the declared revision 36,
selected loft and mixed workspace with millimetre display and category filters.
`scp-workflow-evidence.json` retains executable/report hashes and the complete check list.
No implementation or validation steps remain. The task is ready for normal main integration.

Qualified app: `dist/0.1.7/AnthroForge.dist/AnthroForge.exe` (keep the whole directory).
Companion source: `dist/AnthroForge-0.1.7-source.zip`. The original distribution was
preserved. Raw logs, images, profiles and relocated copies remain ignored local artifacts.

Final source suite: **525 passed**, including queued-writer reprioritization when
workspace membership changes (read-only advisory priority is preserved). Latest
functional fix is 2ff31af: packaged report workers must launch `sys.argv[0]`, since
Nuitka gives `sys.executable` a nonexistent `python.exe` path. The preliminary relocated
test failed with WinError 2; a temporary alias made that same report succeed and was
removed. Source regression verifies the real executable path even when renamed.
The final package passes that actual test without an alias.
Early diagnostic copy: `build/portable-017/early`; final copy: `build/portable-017/final`;
final logs: `build/workflow-017`.

## Recovery inputs

Repo: `E:/development/anthroforge`; setup and validation in `docs/development.md`.
The original recommendation is in chat `01a13b66-cef6-7442-9cd7-7e6d89b93286`,
turn `01a14c9c-90ac-7920-b7fe-b8cf5aff7e2a`; the numbered scope is preserved above.
Qt reference: https://doc.qt.io/qt-6.12/model-view-programming.html
