"""Background recovery discovery and ordinary guarded opening of independent copies."""

from pathlib import Path

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices

from anthroforge.core.jobs import Job


class RecoveryBrowser(QObject):
    changed = Signal()

    def __init__(self, controller, store):
        super().__init__(controller)
        self.controller, self.store = controller, store
        self.rows, self.message, self.busy = [], "", False

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(rows=self.rows, message=self.message, busy=self.busy)

    @Slot()
    def refresh(self):
        if self.busy:
            return
        self.busy, self.message = True, ""
        job = self.make_job()
        job.cleanup = lambda state: self.finished(job, state)
        self.controller.session.scheduler.submit(job)
        self.changed.emit()

    def make_job(self):
        return Job(
            "Find recovery copies",
            frozenset(("@recovery-list",)),
            lambda _: None,
            lambda _, cancel: self.store.scan(),
            self.loaded,
            writes=False,
            kind="project_open",
            publish_during_edit=True,
        )

    def loaded(self, result):
        self.rows, unreadable = result
        self.message = f"{unreadable} unreadable copies remain in the folder." if unreadable else ""

    def finished(self, job, state):
        self.busy = False
        if state == "failed":
            self.message = job.error
        self.changed.emit()

    @Slot(str)
    def openCopy(self, path):
        if any(row["path"] == path for row in self.rows) and self.store.owns(Path(path)):
            self.controller.project_view.requestDocument(path)

    @Slot()
    def showFolder(self):
        try:
            self.store.directory.mkdir(parents=True, exist_ok=True)
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.store.directory))):
                raise OSError(f"Could not open the autosave folder: {self.store.directory}")
        except OSError as error:
            self.controller.message = str(error)
            self.controller.notify()
