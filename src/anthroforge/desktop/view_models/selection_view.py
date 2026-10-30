"""SelectionView owns its QML-facing interaction and presentation contract."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from .. import scene_state
from ..object_selection import ObjectSelection

if TYPE_CHECKING:
    from ..controller import Controller


class SelectionView(QObject):
    changed = Signal()
    selectionChanged = Signal()
    treeChanged = Signal()

    def __init__(self, controller: Controller) -> None:
        super().__init__(controller)
        self.controller = controller
        self.objects = ObjectSelection()
        self.hovered = ""
        self.last_hit: dict[str, Any] = {}
        controller.changed.connect(self.changed)
        controller.selectionChanged.connect(self.selectionChanged)
        controller.treeChanged.connect(self.treeChanged)

    @Property("QVariantList", notify=treeChanged)
    def treeRows(self) -> Any:
        return self.controller.scene_projection.view.value("rows")

    @Property(QObject, constant=True)
    def selectedData(self) -> Any:
        return self.controller.scene_projection.selected

    @Property(QObject, constant=True)
    def sceneChoices(self) -> Any:
        return self.controller.scene_projection.view

    @Property(str, notify=selectionChanged)
    def selectedId(self) -> Any:
        return self.controller.selection

    @Property("QVariantList", notify=selectionChanged)
    def selectedObjects(self) -> Any:
        return self.objects.items

    @Property(str, notify=changed)
    def hoveredId(self) -> Any:
        return self.hovered

    @Slot(str)
    @Slot(str, bool)
    def select(self, entity: Any, extend: Any = False) -> Any:
        self.objects.choose(entity, extend)
        self.publish_selection()

    @Slot("QVariantList")
    def selectObjects(self, identities: Any) -> Any:
        if set(identities) - self.controller.session.document.registry.records.keys():
            raise ValueError("Cannot select an object that is absent from the document.")
        self.objects.replace(identities)
        self.publish_selection()

    @Slot(str)
    def selectSurfaceSources(self, target: Any) -> Any:
        identities = self.controller.run("surface.source_ids", dict(target=target))
        if identities is not None:
            self.selectObjects(identities)

    def publish_selection(self) -> Any:
        if (
            self.controller.session.tissue_preview.target
            and self.controller.session.tissue_preview.target != self.controller.selection
        ):
            from anthroforge.application.tissue_preview import cancel

            cancel(self.controller.session)
        self.controller.scene_projection.synchronize_selection()
        self.controller.scene_projection.publish_records()
        self.controller.authoring.refresh()
        self.controller.notify()

    @Slot(str, result="QVariantMap")
    def objectRecord(self, target: Any) -> Any:
        return (
            self.controller.scene_projection.records.get(target)
            or self.controller.construction.records.get(target)
            or self.controller.mirror_records.get(target, {})
        )

    @Slot("QVariantList", "QVariantList", int, bool, float, result="QVariantMap")
    @Slot("QVariantList", "QVariantList", int, bool, float, bool, result="QVariantMap")
    def pick(
        self,
        origin: Any,
        direction: Any,
        depth: Any,
        select: Any,
        radius: Any = 0.03,
        extend: Any = False,
    ) -> Any:
        hit = scene_state.picked(self.controller, origin, direction, depth, radius)
        self.publish_hit(hit, select, extend)
        return hit

    def publish_hit(self, hit: dict[str, Any], select: bool, extend: bool) -> None:
        previous, self.last_hit = self.hovered, hit
        self.hovered = hit.get("id", "")
        if select:
            self.select(self.hovered, extend)
        if select or previous != self.hovered:
            self.controller.notify()

    @Slot(str)
    def lockAnchor(self, mode: Any) -> Any:
        if self.last_hit.get("id") != self.controller.selection:
            self.controller.message = "Point at a face or vertex on the selected child SCP first."
            self.controller.notify()
            return
        key = "face_lock" if mode == "FACE_CENTER" else "vertex_lock"
        index = self.last_hit["face" if key == "face_lock" else "vertex"]
        self.controller.run(
            "scp.attachment", {"entity": self.controller.selection, "child_mode": mode, key: index}
        )

    @Slot()
    def focusSelection(self) -> Any:
        from ..construction_navigation import focus

        focus(self.controller)
