# Activity presentation optimization — 0.1.5

- Task branch: `codex/activity-panel-015`
- Integration branch: `main`
- Starting revision: `3fa664db4a5661672a93d7d806b03c5fd78f95b0`
- Status: complete
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

The 0.1.4 source/native snapshot is under build/activity-015/baseline. The complete
serial comparison passed: 24 processes, 48 gestures, 120 moves per gesture, normal
and Ctrl snapping, mouse and G-key movement, Activity open and closed. Unrecorded
handler means decreased 55.9–62.1%; all snapping hit counts and undo checks passed.
See [machine-readable evidence](activity-panel-015-evidence.json). All eight recorded
captures stopped cleanly without collector loss; their bounded rings evicted older
events. Retained candidate intervals contain incremental notifications and no Activity
model replacement. Absolute event totals across unequal retained windows are not comparable.

After the comparison, Job.retryable became the shared authority for both describe()
and Activity; the projection also uses Job.active and preserves the empty-name fallback.
These are equivalent-rule ownership cleanups, not another scheduling or UI optimization.
Final candidate confirmation passed all four conditions: eight gestures, handler
means 12.19–14.17 ms, all snapping and undo checks successful. Profiler GUI acceptance
passes F12 during four drag variants, cancellation, text focus/privacy and New/Open.
It now checks incremental Activity notifications instead of requiring the eliminated
hidden-panel binding work. Activity GUI acceptance passed again on 0.1.5; screenshot
visually inspected, including diagnostics, failed/cancelled/succeeded rows and renamed targets.
The first gate had 420 passing tests and one function-length failure in an unfinished
evidence tool. The full gate rerun passed: 421 pytest tests, lint/format, configured
mypy, native build/CTest/style, PowerShell style, numerical checks and native doctor.
The evidence summary/portable assertion updates also pass lint and architecture checks.
The portable build from clean checkpoint ce64fc3 passed relocated minimal-PATH
acceptance: import, attachments, primitives/deformers, deletion, subdivision, saving,
inspection, GPU capture, GUI and desktop/headless runtime reports. Version is 0.1.5.0;
the final desktop capture was inspected. Perfetto imported the snapped/open-panel
trace (84,053 slices) with zero nonzero error statistics. No production code changed
after the build checkpoint; subsequent changes are release documentation.

Deliverables: dist/AnthroForge.dist/AnthroForge.exe (keep its folder together) and
dist/AnthroForge-0.1.5-source.zip (integrity, version and expected source contents checked).
Raw comparison/confirmation/GUI/package logs live
under build/activity-015; profiler gesture captures are under build/profiler-acceptance.
Integration uses the normal task-branch merge/push to main; no PR or history rewrite.

## Ownership review

Coordinator-authored review, separate from test outcomes: ActivityModel owns only a
bounded GUI-thread projection and change notifications. It keeps no Job references,
does not mutate job state and creates no competing queue/timer. Job supplies active
state and the reported Retry-button availability shared with describe(); execution
validation remains in the coordinator. GUI actions still invoke the existing commands.
Core/application/native remain Qt-independent. No geometry algorithms, worker/publication
contracts, undo, saves or profiler lifecycle changed. The render model is deliberately
separate because it owns staged geometry leases, unlike Activity's small value rows.

## Recovery inputs

Use normal Windows setup. Fixture: examples/primitives/cube.obj plus a Body curve.
Raw profiles, snapshots and measurements stay under ignored build/activity-015.
The original user report is local in %LOCALAPPDATA%/AnthroForge/Profiles.
Preserve the unrelated untracked root __init__.py. No subagents are active.
