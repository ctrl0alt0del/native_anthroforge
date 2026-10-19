# Bug and recommendation reporting

- Task branch: `codex/feedback-reports`
- Integration branch: `main`
- Starting revision: `d1cc15d`
- Status: implementation in progress
- Last updated: 2026-10-19, Europe/Bucharest
- Active writer: local desktop chat

## Outcome and acceptance

Help > Report a bug / recommendation and F12 capture the application window before
opening a modal annotation editor. Red rectangles, arrows and text annotate the capture;
a description and Bug/Recommendation category accompany the submission. Reports survive
application upgrades and can be inspected later by the user or an assistant.

## Decisions and ownership

Use a Qt-independent immutable report envelope and replaceable consumer protocol, with
an atomic local ZIP consumer first. Store one `.afreport.zip` per submission under the
user's version-independent AnthroForge/Reports directory. Include JSON, original PNG,
annotated PNG and annotation coordinates. No network submission or project geometry.
Capture/render/input belong to desktop adapters; writing happens in a background worker.
Failures retain the draft for retry. Report activity never changes document revisions,
undo history, checkpoints or calculation scheduling. F12 moves to reporting; Shift+F12
keeps profiling available during edits, alongside the existing Record button.

Qt QQuickWindow::grabWindow, QQuickPaintedItem and QPainter provide capture/painting.
Capture the window before showing the editor, not the desktop or other applications.
Use the existing keyboard manager and Ui controls. Keep every function within 15 lines.
Keep version 0.2.1 for this follow-up build; VCP 0.2.2 remains a separate milestone.

## Verification and next actions

Implement consumer/service, capture/annotation editor, Help/keyboard integration; verify
failure/retry, annotation alignment, cancel/undo isolation and shortcut behavior. Run the
development gate, offscreen GUI/capture checks and relocated portable packaging. Preserve
previous distributions and the unrelated root `__init__.py`. No visible windows or desktop
input. Deliver a separate `dist/0.2.1-reports/AnthroForge.dist` build and corresponding source.

## Implementation checkpoint

Implemented Qt-independent immutable report/annotation records, a replaceable consumer
and destination-neutral receipt, atomic local publication, single background submission,
window capture, one painter for preview/export, and the modal editor. Help/F12 and
Shift+F12 profiling use the keyboard abstraction. Initial desktop smoke has no QML warnings;
five consumer/service tests, architecture checks and mypy on 190 modules pass. Full GUI,
failure/retry, high-DPI evidence, profiler shortcut regression and packaging are pending.
