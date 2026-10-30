"""Recent-project presentation; all opening follows the controller's document safeguards."""

from pathlib import Path

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import projects
from anthroforge.application.autosave import Autosave
from anthroforge.application.preferences import user_path
from anthroforge.application.recent_projects import RecentProjects
from anthroforge.application.recovery import RecoveryStore

from .recovery_browser import RecoveryBrowser


class ProjectLibrary(QObject):
    changed = Signal()
    recoveryRequested = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        path = controller.session.preferences.path
        self.recent = RecentProjects(path.with_name("recent-projects.json") if path else None)
        store = RecoveryStore((path or user_path()).parent / "Autosaves")
        self.autosave = Autosave(store, self.autosaved)
        self.recovery_browser = RecoveryBrowser(controller, store)

    @Property(QObject, constant=True)
    def recoveryBrowser(self):
        return self.recovery_browser

    @Slot()
    def showRecovery(self):
        self.recoveryRequested.emit()

    def autosaved(self, record):
        if record.get("error") or record.get("warning"):
            self.controller.message = "Autosave: " + (record.get("error") or record["warning"])
            self.controller.notify()
        self.changed.emit()

    def poll(self):
        self.autosave.poll(self.controller.session)

    def opened(self, path, lock, revision):
        session = self.controller.session
        if self.autosave.store.owns(Path(path)):
            projects.finish_recovery(session, lock)
            self.controller.message = "Recovery copy opened. Use Save As to keep it."
        else:
            projects.finish_save(session, path, lock, revision)
            self.remember(path)
        self.autosave.reset()

    @Property("QVariantList", notify=changed)
    def recentProjects(self):
        return self.recent.rows()

    @Property(str, notify=changed)
    def error(self):
        return self.recent.error

    def remember(self, path):
        self.perform(lambda: self.recent.remember(path))

    @Slot()
    def clearRecent(self):
        self.perform(self.recent.clear)

    def perform(self, operation):
        try:
            operation()
        except (OSError, ValueError) as error:
            self.controller.message = f"Project history: {error}"
            self.controller.notify()
        self.changed.emit()

    @Slot(str)
    def openRecent(self, path):
        if path not in self.recent.entries:
            return
        self.controller.project_view.requestDocument(path)
