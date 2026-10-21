"""Desktop notifications adapt the same read-only export job used by headless clients."""

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices

from .controller_actions import local_path


class InspectionExport(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.job, self.path, self.message = controller, None, "", ""

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(busy=bool(self.job and self.job.active), message=self.message, path=self.path)

    @Slot(str)
    def start(self, path):
        owner = self.controller
        result = owner.run(
            "inspection.export",
            self.options(path),
        )
        if result:
            self.job = next(j for j in owner.session.scheduler.jobs if j.id == result["job"])
            self.path, self.message = (
                result["path"],
                "Exporting frozen revision " + str(result["revision"]),
            )
            self.changed.emit()

    def options(self, path):
        owner, tool = self.controller, self.controller.tissue_inspection
        tissue = dict(
            stage=tool.stage, reference=tool.reference, mode=tool.mode, finding=tool.finding
        )
        return dict(
            path=local_path(path),
            selected=owner.selection,
            editing=owner.authoring.editing,
            tissue=tissue if tool.target else None,
        )

    def synchronize(self):
        if self.job is None or self.job.active:
            return
        self.message = (
            "Inspection report saved: " + self.path
            if self.job.state == "succeeded"
            else "Inspection export " + self.job.state + ": " + self.job.error
        )
        self.job = None
        self.controller.message = self.message
        self.changed.emit()

    @Slot()
    def showFolder(self):
        from pathlib import Path

        if self.path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(self.path).parent)))
