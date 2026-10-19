"""On-demand inbox I/O; one owned preview and no idle polling or document mutations."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from functools import partial

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot
from PySide6.QtGui import QImage

from anthroforge.feedback.inbox import ReportInbox

from .record_model import RecordModel
from .report_image import load_preview


class ReportBrowser(QObject):
    changed = Signal()

    def __init__(self, parent, inbox: ReportInbox):
        super().__init__(parent)
        self.inbox = inbox
        self.model = RecordModel(self, ("key", "title", "category", "created_at", "error"), "key")
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="report-inbox")
        self.future, self.action, self.error = None, "", ""
        self.key, self.description, self.location, self._image = "", "", "", QImage()
        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self.poll)

    @Property(QObject, constant=True)
    def reports(self):
        return self.model

    @Property(QImage, notify=changed)
    def image(self):
        return self._image

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            busy=self.future is not None,
            action=self.action,
            error=self.error,
            key=self.key,
            description=self.description,
            location=self.location,
            count=len(self.model.rows),
            width=self._image.width(),
            height=self._image.height(),
        )

    def start(self, action, work):
        if self.future is not None:
            return
        self.action, self.error = action, ""
        self.future = self.executor.submit(work)
        self.timer.start()
        self.changed.emit()

    @Slot()
    def refresh(self):
        self.start("list", self.inbox.entries)

    @Slot(str)
    def select(self, key):
        if self.future is not None or not any(row["key"] == key for row in self.model.rows):
            return
        self.clear_preview()
        self.key = key
        self.start("read", partial(load_preview, self.inbox, key))

    @Slot(str)
    def deleteReport(self, key):
        if key and key == self.key:
            self.start("delete", partial(self.inbox.delete, key))

    def poll(self):
        if self.future is None or not self.future.done():
            return
        future, self.future = self.future, None
        self.timer.stop()
        try:
            self.accept(future.result())
        except Exception as error:
            self.error = str(error) or type(error).__name__
        self.changed.emit()

    def accept(self, result):
        if self.action == "list":
            self.model.synchronize_records([asdict(row) for row in result])
            self.select_available()
        elif self.action == "read":
            detail, self._image = result
            self.description, self.location = detail.description, detail.location
        elif self.action == "delete":
            self.model.remove_missing({row["key"] for row in self.model.rows} - {self.key})
            self.select_available()

    def select_available(self):
        keys = [row["key"] for row in self.model.rows]
        if keys:
            self.select(self.key if self.key in keys else keys[0])
        else:
            self.clear_preview()

    def clear_preview(self):
        self.key, self.description, self.location, self._image = "", "", "", QImage()

    @Slot()
    def dismiss(self):
        if self.future is None:
            self.clear_preview()
            self.model.synchronize_records([])
            self.error = ""
            self.changed.emit()

    def close(self):
        self.timer.stop()
        self.executor.shutdown(wait=True)
