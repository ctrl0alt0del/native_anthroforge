"""ProjectView owns its QML-facing interaction and presentation contract."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from .. import controller_actions as actions
from .. import project_actions
from ..project_library import ProjectLibrary

if TYPE_CHECKING:
    from ..controller import Controller


class ProjectView(QObject):
    changed = Signal()
    saveChoiceRequested = Signal(str)
    discardRequested = Signal(str)
    closeReady = Signal()

    def __init__(self, controller: Controller) -> None:
        super().__init__(controller)
        self.controller = controller
        controller.changed.connect(self.changed)
        controller.saveChoiceRequested.connect(self.saveChoiceRequested)
        controller.discardRequested.connect(self.discardRequested)
        controller.closeReady.connect(self.closeReady)

    @Property(str, notify=changed)
    def documentName(self) -> str:
        return self.controller.session.document.name

    @Property(str, notify=changed)
    def documentId(self) -> str:
        return str(self.controller.session.document.id)

    @Slot(str)
    def afterSave(self, action: Any) -> Any:
        self.after_save = action

    @Slot(str, float, str, bool)
    def importMesh(self, path: Any, units: Any, parent: Any, y_up: Any) -> Any:
        result = self.controller.run(
            "import",
            {"path": actions.local_path(path), "units": units, "parent": parent, "y_up": y_up},
        )
        if result:
            self.controller.message = "Import queued. You can keep navigating and editing."

    @Slot(str, str)
    def saveProject(self, path: Any, policy: Any) -> Any:
        try:
            project_actions.save(self.controller, path, policy)
        except Exception as error:
            self.controller.message = str(error)
            self.controller.session.waiting_save = False
            self.controller.notify()

    @Slot()
    def cancelSaveWait(self) -> Any:
        for job in self.controller.session.scheduler.active_jobs:
            if job.active and "@document" in job.outputs:
                self.controller.session.scheduler.cancel_job(job.id)
        self.pending_save = ""
        self.after_save = None
        self.pending_document = None
        self.controller.session.waiting_save = False
        self.controller.notify()

    @Slot(str)
    def requestDocument(self, path: Any) -> Any:
        if self.controller.session.document.revision != self.controller.session.saved_revision:
            self.controller.discardRequested.emit(path)
        else:
            self.replaceDocument(path)

    @Slot(str)
    def replaceDocument(self, path: Any) -> Any:
        project_actions.queue_document(self.controller, path)

    @Slot()
    def newDocument(self) -> None:
        self.requestDocument("")

    def initialize(self) -> None:
        self.pending_save, self.pending_document = "", None
        self.temporary_locks = []
        self.after_save = None
        self.library = ProjectLibrary(self.controller)
