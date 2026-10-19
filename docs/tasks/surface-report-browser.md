# Selection-based surfaces and report browser

- Task branch: `codex/surface-report-browser`
- Integration branch: `main`
- Starting revision: `7af77fd`
- Status: in progress
- Last updated: 2026-10-19, Europe/Bucharest
- Active writer: desktop chat, direct work

## Outcome and acceptance

Extend the Patch toolbar action: one closed curve creates a patch; two or more
selected curves/fibers create a standalone loft surface. Preserve source validation,
closed-loop correspondence preview and accepted asynchronous creation selection.
Add Help access to existing feedback reports, description/screenshot preview and
explicit deletion. Keep the local inbox independent of app versions and replaceable.

## Decisions and relevant files

Surface construction already exists in shared operations; desktop creation routing
owns the selection-dependent entry point. Reports currently support submission only;
introduce a separate narrow inbox contract rather than burdening every consumer with
read/delete capabilities. Keep filesystem/archive work off the UI thread and use a
bounded scrolling report list. See engineering guidelines and feedback_reports.md.

## Current state

Inspected toolbar, creation lifecycle, surface commands and feedback storage/service.
No implementation yet. Existing untracked root __init__.py remains untouched.

## Verification

Official Qt ListView/reuseItems and Qt Quick performance documentation reviewed.
Pending unit/contract tests, actual offscreen QML interaction, development gate,
relocated portable qualification and source archive. No visible windows or desktop
input; offscreen checks do not establish interactive acceptance on the user's GPU.

## Next actions and blockers

1. Implement shared surface selection entry and separate feedback inbox/browser.
2. Exercise creation, preview, report loading, deletion and failure paths.
3. Checkpoint, run gate/package checks, update docs, merge and push normally.

## Recovery inputs

No external assets required. Use isolated temporary report inboxes for deletion tests;
never delete the user's actual reports as part of acceptance.
