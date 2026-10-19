"""Opt-in packaged feedback qualification; captures the real QML window."""

import json
from pathlib import Path
from time import monotonic

from PySide6.QtCore import QEvent, QObject, Qt, QTimer
from PySide6.QtGui import QGuiApplication, QKeyEvent

from anthroforge.feedback.storage import LocalReportConsumer


class FeedbackProbe(QObject):
    def __init__(self, app, controller, engine, output):
        super().__init__(app)
        self.app, self.controller, self.window = app, controller, engine.rootObjects()[0]
        self.output, self.started = Path(output), monotonic()
        self.before, self.cursor = controller.session.document, controller.session.history.cursor
        self.editor = controller.feedback
        self.editor.service.consumer = LocalReportConsumer(self.output.parent / "feedback-inbox")
        self.editor.ready.connect(self.annotate)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(40)
        QTimer.singleShot(300, self.start)

    def start(self):
        for kind in (QEvent.KeyPress, QEvent.KeyRelease):
            QGuiApplication.sendEvent(self.window, QKeyEvent(kind, Qt.Key_F12, Qt.NoModifier))

    def annotate(self):
        QTimer.singleShot(0, self.submit)  # Capture must finish before editing is enabled.

    def submit(self):
        try:
            for kind, text in (("rectangle", ""), ("arrow", ""), ("text", "Portable report")):
                assert self.editor.begin(120, 120, kind, text, 1)
                self.editor.extend(380, 270)
                self.editor.finishStroke()
            self.editor.submit("bug", "Portable feedback capture and annotation acceptance.")
        except Exception as error:
            self.finish(str(error))

    def poll(self):
        if monotonic() - self.started > 20:
            self.finish("Feedback probe timed out: " + self.controller.message)
        elif self.editor.service.state == "failed":
            self.finish(self.editor.service.error)
        elif self.editor.service.state == "saved":
            changed = self.controller.session.document is not self.before
            changed |= self.controller.session.history.cursor != self.cursor
            self.finish("Feedback changed document history" if changed else "")

    def finish(self, error):
        self.timer.stop()
        result = dict(passed=not error, error=error, report=self.editor.service.location)
        result.update(width=self.editor.image.width(), height=self.editor.image.height())
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.output.write_text(json.dumps(result), encoding="utf-8")
        self.app.exit(1 if error else 0)
