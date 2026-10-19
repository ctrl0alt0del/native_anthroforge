# Bug and recommendation reporting

- Task branch: `codex/feedback-reports`
- Integration branch: `main`
- Starting revision: `d1cc15d`
- Status: implementation and qualification complete; ready for validated main integration
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

## Verification scope

Consumer/service, capture/annotation editor, Help/keyboard integration, failure/retry,
annotation alignment, cancel/undo isolation and shortcut behavior are implemented and
verified. Development gate, offscreen GUI/capture checks and relocated portable packaging
pass. Preserve
previous distributions and the unrelated root `__init__.py`. No visible windows or desktop
input. Deliver a separate `dist/0.2.1-reports/AnthroForge.dist` build and corresponding source.

## Implementation checkpoint

Implemented Qt-independent immutable report/annotation records, a replaceable consumer
and destination-neutral receipt, atomic local publication, single background submission,
window capture, one painter for preview/export, and the modal editor. Help/F12 and
Shift+F12 profiling use the keyboard abstraction. Initial desktop smoke has no QML warnings;
five consumer/service tests, architecture checks and mypy on 190 modules pass. Full QML
acceptance now passes normal and 200% DPI: menu/F12, capture before modal, rectangles,
arrows/text, undo, zoom/scroll alignment, failed save/retry, PNG fidelity, repeated/canceled
reports and reporting from another modal. The final shortcut uses application scope for
the explicit reporting binding so Qt popups do not suppress it; it is not an OS hotkey.
Five Shift+F12 profiler drag trials pass, including Ctrl snapping, Activity open/closed,
cancellation, focus/privacy and New/Open. The synthetic modifier-release test needed an
explicit held mask because enum inversion incorrectly cleared Ctrl; no production input
policy changed to accommodate that test. Source packaged-probe path also passes.

Full Windows development gate passes at `5768250`: 901 tests, native build/three CTests,
static analysis, types, formatting, function limits and runtime doctor. Narrow 1050×680
layout and 200% DPI, including zoom/scroll marking, pass and captures were inspected.
Ownership review is recorded in development_status.md. No visible UI was used.

Final failure-path check found that capture errors emitted a notification without updating
the controller's stable property projection. Reproduced an empty displayed status despite
the error string, then routed it through `Controller.notify()`. Offscreen acceptance now
asserts the displayed error and released draft, followed by successful profiling; all
901 tests pass again. The first `963eaba` packaging candidate was superseded by clean
`bcd72f7`, which includes this correction.

## Final delivery evidence

`dist/0.2.1-reports/AnthroForge.dist/AnthroForge.exe` is the final clean `bcd72f7` build.
The entire distribution was copied to a fresh temporary directory and the complete
`tools/check_portable.py --offscreen` suite passed with a minimal PATH. Its report probe
captured the window, opened the editor, painted all three mark types, saved a portable
ZIP and retained document/history state. Archive contents and all 94 QML/JS/SVG assets
were verified. See `build/feedback-portable-final/portable-check.json`,
`build/feedback-regression-final.log` and `build/feedback-package-final.log`.

No visible windows or desktop input were used. The extra never-shown Windows-window
experiment captured UI but omitted Quick3D mesh pixels; it is not GPU-window acceptance.
The separate existing hidden QQuickRenderControl geometry check passes. Hands-on
ordinary-window capture remains unverified. This is a validation limit, not evidence of
a defect in the ordinary visible-window capture API.

Publish the matching `dist/AnthroForge-0.2.1-reports-source.zip`, merge this validated
branch into the unchanged integration main and push normally. The final integration
commit is discoverable through Git ancestry; local build evidence stays ignored. Preserve
the prior 0.2.1 artifacts and unrelated root `__init__.py`.
