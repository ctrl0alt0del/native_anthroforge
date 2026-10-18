# SCP workflow improvements, 0.1.7

- Task branch: `codex/scp-workflow-improvements`
- Integration branch: `main`
- Starting revision: `e8565e28328a205f10575f03928737ccd782d0d1`
- Status: implementation in progress
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
These are application foundations; desktop integration and report export remain in progress.

## Verification

Baseline is 0.1.6 with 512 tests plus GUI/profiler/portable qualification. New behavior
requires focused API tests, actual GUI interactions and snapshot consistency checks,
the development gate, ownership review, and relocated portable qualification.

First checkpoint: 518 tests pass; strict mypy passes. Added native-anchor read-only
inspection, cycle/downstream distinction, 3,000-output graph, mixed workspace
round-trip and policy guard coverage. No GUI or release acceptance claimed yet.

## Next actions

1. Integrate inspector, workspace management/category filters and dimensional UI fields.
2. Implement frozen inspection export using existing offscreen GPU capture and add CLI/UI.
3. Qualify 0.1.7, archive corresponding source, merge/push normally after all checks pass.

## Recovery inputs

Repo: `E:/development/anthroforge`; setup and validation in `docs/development.md`.
The original recommendation is in chat `01a13b66-cef6-7442-9cd7-7e6d89b93286`,
turn `01a14c9c-90ac-7920-b7fe-b8cf5aff7e2a`; the numbered scope is preserved above.
Qt reference: https://doc.qt.io/qt-6.12/model-view-programming.html
