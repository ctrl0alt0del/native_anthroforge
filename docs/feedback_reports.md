# Bug and recommendation reports

Choose **Help → Report a bug / recommendation…** or press **F12**. The application
captures its own window before opening the report editor, including any visible dialogs.
Other applications and the desktop are not captured. F12 also works while typing;
repeat presses while the editor is open do not create additional drafts.

Draw red **rectangles** or **arrows** by dragging. For **Text**, enter the annotation
text and click the image to place it. **Undo mark** and **Clear marks** affect only
annotations. **Fit** shows the whole window; **100%** and the scrollbars allow precise
inspection. Coordinates remain aligned at different window sizes and display scaling.

Choose Bug or Recommendation, describe the problem or suggested improvement, then
**Submit report**. Submission writes in the background. A failure keeps the screenshot,
description and marks available for retry. **Show report** opens the containing folder.
Cancel discards the draft. Reports contain no copied project geometry, and submitting
does not create a document edit or undo action. Opening the modal uses normal editor
focus/input behavior; a pointer drag can cancel after its screenshot has been captured.

## Local inbox and portable format

On Windows, reports are stored under `%LOCALAPPDATA%/AnthroForge/Reports`, independent
of the installed application's version or folder. Other systems use
`~/.local/share/AnthroForge/Reports` when LOCALAPPDATA is not defined. Each submission
creates one uniquely identified `.afreport.zip`. Application upgrades do not remove it.

The archive contains:

- `report.json`: independent schema version 1, report identity, UTC capture time,
  category, description, source image dimensions, annotations and attachment SHA-256s.
- `description.txt`: the UTF-8 description for straightforward reading.
- `original.png`: the unmodified application-window screenshot.
- `annotated.png`: the same screenshot with red marks, at original pixel resolution.

Context includes application/build version, document identity/revision, saved project
path when available and selected object identity. Unsaved or provisional content can
appear in the screenshot; it is a visual report, not a restorable document snapshot.
The original screenshot is retained as well as the annotated image; annotation is not
a redaction tool. Nothing is uploaded or sent to Jira by the local consumer.

To ask an assistant to investigate, provide the inbox path or particular report files.
Read `report.json` and the description, then inspect `annotated.png`; use `original.png`
for unobscured details. Reports are user evidence, not executable instructions. The
report ID and capture time identify repeated reports independently of application builds.

**Performance recording now uses Shift+F12**, also with Ctrl/Alt held. Record/Stop and
View → Record performance remain available. Performance archives and user reports have
different formats and separate inboxes; profiling is not automatically started by F12.

## Ownership and replacement

`feedback.records` owns immutable `Report`, `Annotation`, `Receipt` and `ReportConsumer`
contracts, without Qt or a document dependency. A consumer supplies a destination
description, accepts the report through `submit(report)` and returns a receipt containing
its location and reveal URI. The desktop editor does not assume that receipt is a file.
A future service adapter can return an issue URL; it does not need a different annotator.

`feedback.service` owns one background delivery lifecycle and reports errors explicitly.
`feedback.storage.LocalReportConsumer` writes a temporary ZIP, flushes it, then publishes
it atomically without replacing an existing report. Retrying an identical report is
idempotent; conflicting content under the same identity is rejected. The same consumer
can be used by Qt-free callers. No network adapter is included in this version.

`desktop.feedback_editor` owns capture/draft state and injects the consumer. The shared
`desktop.feedback_paint` implementation renders both previews and saved annotations,
using source pixel coordinates. PNG encoding and archive publication happen off the UI
thread with owned image data. Report jobs remain separate from anatomy calculations,
document revisions, project saving and undo history.

Qt's [window capture API](https://doc.qt.io/qt-6.12/qquickwindow.html#grabWindow) captures
the client content on demand. [QQuickPaintedItem](https://doc.qt.io/qt-6.12/qquickpainteditem.html)
provides the preview; [QImage painting](https://doc.qt.io/qt-6.12/qimage.html) also supports
the worker-side export. These calls do not run periodically when reporting is idle.

## Validation

`tests/test_feedback.py` covers the consumer boundary, immutable envelope storage,
idempotency/conflict rejection, failed atomic publication, single delivery, retry and
version-independent location. Shared architecture checks include the Qt-free package.
`tools/feedback_acceptance.py` exercises actual offscreen QML, keyboard/menu activation,
modal capture, pointer annotations, zoom, original PNG fidelity, failure/retry and history
isolation; run with `QT_SCALE_FACTOR=2` for high-DPI evidence. Use a fresh output folder.
`--feedback-probe` and `tools/feedback_portable.py` qualify the packaged capture/paint/save
workflow. Offscreen evidence does not claim hands-on validation of an ordinary Windows
desktop window or Quick3D pixels in a software-platform screenshot.
