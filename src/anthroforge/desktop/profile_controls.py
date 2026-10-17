"""Small runtime-only UI adapter: recording never enters an editing transaction."""

from pathlib import Path

from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices


class ProfileControls(QObject):
    changed = Signal()

    def __init__(self, controller, collector):
        super().__init__(controller)
        self.profiler = controller.session.profiler
        self.profiler.collector = collector
        self._state = self.profiler.status()
        self.timer = QTimer(self)
        self.timer.setInterval(250)
        self.timer.timeout.connect(self.refresh)

    @Property("QVariantMap", notify=changed)
    def state(self):
        return self._state

    @Slot()
    def toggle(self):
        try:
            if self.profiler.state in ("recording", "export_failed"):
                self.profiler.stop()
            elif self.profiler.state in ("idle", "saved"):
                self.profiler.start()
            self.timer.start()
            self.refresh()
        except Exception as error:
            self._state = dict(self.profiler.status(), error=str(error))
            self.changed.emit()

    @Slot()
    def refresh(self):
        self._state = self.profiler.status()
        if self._state["state"] in ("idle", "saved", "export_failed"):
            self.timer.stop()
        self.changed.emit()

    @Slot()
    def reveal(self):
        path = self.profiler.path
        if path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(path).parent)))
