"""Packaged collector qualification, enabled only by the explicit diagnostic argument."""

import json
from pathlib import Path

from PySide6.QtCore import QObject, QTimer


class ProfileProbe(QObject):
    def __init__(self, app, controller, output):
        super().__init__(app)
        self.app, self.controller, self.output = app, controller, Path(output)
        self.index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.step)
        QTimer.singleShot(700, self.start)

    def start(self):
        self.controller.session.command("profile.start")
        self.timer.start(30)

    def step(self):
        self.controller.notify()
        self.index += 1
        if self.index == 40:
            self.timer.stop()
            self.controller.session.command(
                "profile.stop", path=str(self.output.with_suffix(".afprofile.zip"))
            )
            QTimer.singleShot(400, self.finish)

    def finish(self):
        if not self.controller.session.profiler.done.is_set():
            QTimer.singleShot(100, self.finish)
            return
        report = self.controller.session.profiler.status()
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.output.write_text(json.dumps(report), encoding="utf-8")
        self.app.quit()
