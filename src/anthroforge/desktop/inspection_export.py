"""Desktop notifications adapt the same read-only export job used by headless clients."""

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices

from .controller_actions import local_path


class InspectionExport(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.job, self.path, self.message = controller, None, "", ""
        self.replay = False

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
        return dict(
            path=local_path(path),
            selected=owner.selection,
            editing=owner.authoring.editing,
            tissue=self.tissue_options() if tool.target else None,
            route=owner.route_inspection.state if owner.route_inspection.visible else None,
            replay=self.replay and owner.session.shortcut_comparison.baseline is not None,
            spatial=self.spatial_options(),
        )

    @Slot(bool)
    def includeReplay(self, enabled):
        self.replay = enabled

    def spatial_options(self):
        owner, view = self.controller, self.controller.neighborhood
        return dict(
            finding=owner.spatial_evidence.row or None,
            measurements=bool(owner.surface_measurements.report),
            **{owner.placement_inspection.kind: bool(owner.placement_inspection.report)},
            neighborhood=view.target if view.members else "",
            camera=view.view_camera[0] if view.view_camera else None,
            orthographic=view.view_camera[1] if view.view_camera else False,
        )

    def tissue_options(self):
        owner, tool = self.controller, self.controller.tissue_inspection
        return dict(
            stage=tool.stage,
            reference=tool.reference,
            mode=tool.mode,
            finding=tool.finding,
            section=owner.section_tools.state,
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
