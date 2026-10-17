# Activity presentation optimization — 0.1.5

- Task branch: `codex/activity-panel-015`
- Integration branch: `main`
- Starting revision: `3fa664db4a5661672a93d7d806b03c5fd78f95b0`
- Status: in progress
- Last updated: 2026-10-17, Europe/Bucharest
- Active writer: desktop implementation chat

## Outcome and acceptance

Replace Activity list rebuilding with stable incremental presentation. Preserve job
ordering, elapsed/progress/error details, target names, diagnostics, cancel/retry,
document switching, scheduler/undo/checkpoint contracts and profiler operation.
Release 0.1.5 after development, actual GUI, comparative performance and portable checks.

## Evidence and ownership

[Prior investigation](snap-drag-investigation.md) isolated repeated Activity model
replacement. The user's packaged 0.1.4 report 20261017-194922-5594a094 shows 170 Activity
model replacements in 9.03 seconds, 13 ms average binding time, and native picking
averaging 0.072 ms. It does not establish a twofold Ctrl-specific handler slowdown.

The desktop owns a stable QAbstractListModel and separate inexpensive summary properties.
Rows retain job identity and update changed roles only; scheduler policy stays in the
existing coordinator. Keep the existing recent-history scope and lifecycle controls.
Follow [engineering guidelines](../engineering_guidelines.md), including 15-line functions.

## Current state and next steps

Stable ActivityModel and lightweight job projection are integrated. The header reads
change-only summary properties; diagnostics metrics have their own notification.
Recent-history scope remains 40 jobs. Six model tests plus architecture checks pass;
Qt's model tester checks insert/move/remove contracts. Actual GUI cancel/retry, failure,
target rename, hidden updates and New pass. Screenshot inspected. The first recorded
modal pilot has no Activity model replacements, only incremental row notifications.

The 0.1.4 source/native snapshot is under build/activity-015/baseline. Next: serial
counterbalanced comparisons, complete profiler/gesture acceptance, full gate and
portable/source release. Performance improvement is not yet qualified by repeated trials.

## Recovery inputs

Use normal Windows setup. Fixture: examples/primitives/cube.obj plus a Body curve.
Raw profiles, snapshots and measurements stay under ignored build/activity-015.
The original user report is local in %LOCALAPPDATA%/AnthroForge/Profiles.
Preserve the unrelated untracked root __init__.py. No subagents are active.
