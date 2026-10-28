"""Restoreable viewport isolation with a private camera; never a new workspace."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import inspection_neighborhood
from anthroforge.native import scene

from . import scene_projection
from .tissue_finding_view import camera_frame


class NeighborhoodTools(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.members, self.target = controller, frozenset(), ""
        self.camera, self.context, self.explanation = None, None, ""
        self.view_camera = None

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            active=bool(self.members),
            count=len(self.members),
            target=self.target,
            explanation=self.explanation,
        )

    @Slot()
    def inspect(self):
        owner, session = self.controller, self.controller.session
        if session.history.before is not None or session.waiting_save or not owner.selection:
            return
        result = inspection_neighborhood.describe(session, owner.selection)
        if not self.members:
            self.camera = (list(session.workspace.camera), session.workspace.orthographic)
            self.view_camera = self.camera
        self.target, self.members = result["target"], frozenset(result["members"])
        self.context, self.explanation = self.signature(), result["explanation"]
        self.publish()
        self.frame()

    def signature(self):
        session = self.controller.session
        return session, session.document.id, session.active_workspace

    def publish(self):
        scene_projection.publish(self.controller)
        self.controller.construction.points.synchronize(self.controller.construction.records)
        self.changed.emit()

    def frame(self):
        rows = [r for r in self.controller._render_rows if r["surface_visible"] and r["handle"]]
        if rows:
            frames = [
                scene.geometry_matrix(
                    self.controller.session.engine, r["matrix"], r["geometry_offset"]
                )
                for r in rows
            ]
            bounds = scene.bounds(
                self.controller.session.engine, [r["handle"] for r in rows], frames
            )
            self.controller.frameRequested.emit(camera_frame(bounds))

    def synchronize(self):
        if self.members and self.signature() != self.context:
            self.clear(False)

    @Slot()
    def restore(self):
        self.clear(True)

    def clear(self, camera):
        saved = self.camera
        self.members, self.target, self.camera, self.context = frozenset(), "", None, None
        self.publish()
        if camera and saved:
            self.controller.cameraRequested.emit(*saved)

    def restore_capture(self, row, camera, orthographic):
        self.target, self.members = row["target"], frozenset(row["members"])
        self.camera = self.view_camera = (camera, orthographic)
        self.context = self.signature()
        self.publish()
