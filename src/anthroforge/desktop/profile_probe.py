"""Packaged collector qualification, enabled only by the explicit diagnostic argument."""

import json
from collections import Counter
from pathlib import Path

from PySide6.QtCore import QObject, QTimer


class ProfileProbe(QObject):
    def __init__(self, app, controller, output):
        super().__init__(app)
        self.app, self.controller, self.output = app, controller, Path(output)
        self.events, self.index = [], 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.step)
        QTimer.singleShot(700, self.start)

    def start(self):
        self.controller.qt_profiler.start()
        self.timer.start(30)

    def step(self):
        self.controller.notify()
        self.events.extend(self.controller.qt_profiler.drain())
        self.index += 1
        if self.index == 40:
            self.timer.stop()
            self.controller.qt_profiler.stop()
            QTimer.singleShot(400, self.finish)

    def finish(self):
        self.events.extend(self.controller.qt_profiler.drain())
        report = dict(status=self.controller.qt_profiler.status(), events=self.events)
        report["categories"] = dict(Counter(e["cat"] for e in self.events))
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.output.write_text(json.dumps(report), encoding="utf-8")
        self.app.quit()
