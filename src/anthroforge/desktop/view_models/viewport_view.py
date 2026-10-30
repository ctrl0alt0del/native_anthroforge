"""ViewportView owns its QML-facing interaction and presentation contract."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.native import scene

from .. import controller_actions as actions

if TYPE_CHECKING:
    from ..controller import Controller


class ViewportView(QObject):
    changed = Signal()
    frameRequested = Signal(list)
    cameraRequested = Signal(list, bool)

    def __init__(self, controller: Controller) -> None:
        super().__init__(controller)
        self.controller = controller
        controller.changed.connect(self.changed)
        controller.frameRequested.connect(self.frameRequested)
        controller.cameraRequested.connect(self.cameraRequested)

    @Slot(bool)
    def setViewportProjection(self, orthographic: Any) -> Any:
        self.orthographic = orthographic

    @Slot(list)
    def setViewportDirection(self, direction: Any) -> Any:
        self.direction = tuple(direction)

    @Property(QObject, constant=True)
    def meshModel(self) -> Any:
        return self.controller.render_model

    @Property(QObject, constant=True)
    def pathModel(self) -> Any:
        return self.controller.path_model

    @Property(QObject, constant=True)
    def fiberDisplayModel(self) -> Any:
        return self.controller.fiber_display.model

    @Property(QObject, constant=True)
    def imageModel(self) -> Any:
        return self.controller.image_model

    @Slot(str, result=QObject)
    def imageLayer(self, depth: Any) -> Any:
        return self.controller.image_layers[depth]

    @Property(QObject, constant=True)
    def constructionModel(self) -> Any:
        return self.controller.construction.browser

    @Property(QObject, constant=True)
    def pointModel(self) -> Any:
        return self.controller.construction.points.model

    @Property(QObject, constant=True)
    def markerModel(self) -> Any:
        return self.controller.marker_model

    @Property("QVariantList", notify=changed)
    def markerRows(self) -> Any:
        from ..inspection_visibility import records
        from ..mirror_scene import presented

        values = [*self.controller.rows, *self.controller.mirror_records.values()]
        return [
            v
            for v in records(self.controller, values)
            if not v.get("asset")
            and (not v.get("is_construction"))
            and (not v.get("is_tissue"))
            and presented(self.controller, v)
        ]

    @Slot()
    def cancelViewportTools(self, keep: Any = None) -> Any:
        tools = (
            self.controller.inspection_tools,
            self.controller.image_tools,
            self.controller.drawing_tools,
            self.controller.tissue_region_tools,
            self.controller.tissue_inspection,
            self.controller.tissue_painting,
        )
        for tool in (*tools, self.controller.placement_inspection):
            if tool is not keep:
                tool.cancel()

    def restore_camera(self) -> Any:
        identity = (
            str(self.controller.session.document.id),
            self.controller.session.active_workspace,
        )
        if identity != self.camera_workspace:
            self.camera_workspace = identity
            self.controller.cameraRequested.emit(
                list(self.controller.session.workspace.camera),
                self.controller.session.workspace.orthographic,
            )

    @Slot("QVariantList", bool)
    def saveCamera(self, values: Any, orthographic: Any) -> Any:
        if self.controller.neighborhood.members:
            self.controller.neighborhood.view_camera = (list(values), orthographic)
        if (
            not self.controller.session.waiting_save
            and (not self.controller.capture_mode)
            and (not self.controller.neighborhood.members)
        ):
            self.controller.session.command(
                "workspace.update", camera=values, orthographic=orthographic
            )

    @Slot(str, result=bool)
    def beginTransform(self, mode: Any) -> Any:
        try:
            actions.start_transform(self.controller, mode)
            return self.controller.session.history.before is not None
        except Exception as error:
            self.controller.message = str(error)
            self.controller.notify()
            return False

    @Slot()
    @Slot(str)
    def rebaseTransform(self, mode: Any = "") -> Any:
        actions.rebase_transform(self.controller, mode)

    @Slot(result="QVariantList")
    def selectionCenter(self) -> Any:
        return actions.selection_center(self.controller)

    @Slot("QVariantList", float, result="QVariantList")
    def rotationDelta(self, axis: Any, angle: Any) -> Any:
        return [0, 0, 0, *scene.axis_rotation(self.controller.session.engine, axis, angle), 1, 1, 1]

    @Slot(int, float)
    def dragTransform(self, axis: Any, amount: Any) -> Any:
        actions.drag_transform(self.controller, axis, amount)

    @Slot("QVariantList")
    def transformDelta(self, values: Any) -> Any:
        actions.transform_delta(self.controller, values)

    @Slot(bool)
    def endTransform(self, cancel: Any) -> Any:
        actions.end_transform(self.controller, cancel)

    @Slot()
    def frameSelection(self) -> Any:
        actions.frame(self.controller)
