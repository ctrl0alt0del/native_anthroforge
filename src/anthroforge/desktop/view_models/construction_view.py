"""ConstructionView owns its QML-facing interaction and presentation contract."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Property, QObject, Signal, Slot

if TYPE_CHECKING:
    from ..controller import Controller


class ConstructionView(QObject):
    changed = Signal()

    def __init__(self, controller: Controller) -> None:
        super().__init__(controller)
        self.controller = controller
        controller.changed.connect(self.changed)

    @Property("QVariantMap", notify=changed)
    def conversionState(self) -> Any:
        from anthroforge.application.curve_conversion import status

        return status(self.controller.session)

    @Property("QVariantMap", notify=changed)
    def surfacePreview(self) -> Any:
        from anthroforge.application.surface_preview import status

        return status(self.controller.session)

    @Property("QVariantMap", notify=changed)
    def tissuePreview(self) -> Any:
        from anthroforge.application.tissue_preview import status

        from ..values import qml

        return qml(status(self.controller.session))

    @Slot(result="QVariantList")
    def ordinaryParents(self) -> Any:
        from ..image_tools import parent_choices

        return parent_choices(self.controller)

    @Slot(str)
    def createSurface(self, kind: Any) -> Any:
        from ..construction_creation import surface

        surface(self.controller, kind)

    @Slot(str)
    def editConstruction(self, target: Any) -> Any:
        from ..construction_navigation import edit

        edit(self.controller, target)

    @Slot(result="QVariantList")
    def tissueSources(self) -> Any:
        from ..construction_navigation import tissue_sources

        return tissue_sources(self.controller)

    @Slot()
    def createPoint(self) -> Any:
        from ..image_tools import context_owner

        target = self.controller.run(
            "construction.point.create", {"owner": context_owner(self.controller)}
        )
        if target:
            self.controller.selection_view.select(target)

    @Slot(result="QVariantList")
    def surfaceRoles(self) -> Any:
        from ..surface_choices import rows

        return rows(self.controller)

    @Slot(result="QVariantList")
    def stackingTissues(self) -> Any:
        from ..tissue_projection import choices

        return choices(self.controller)

    @Property("QVariantMap", notify=changed)
    def surfaceAction(self) -> Any:
        from ..construction_creation import surface_action

        return surface_action(self.controller)

    @Slot(str, str, result="QVariantMap")
    def surfaceOptions(self, target: Any, boundary: Any) -> Any:
        from ..surface_tools import choices

        return choices(self.controller, target, boundary)

    @Slot(result="QVariantList")
    def anatomicalSurfaces(self) -> Any:
        from anthroforge.core.results import geometry_asset

        return [
            dict(id=item.id, name=item.name)
            for item in self.controller.session.document.entities
            if geometry_asset(item)
        ]

    @Slot(QObject, result=QObject)
    def createChoiceModel(self, owner: Any) -> Any:
        from ..choice_model import ChoiceModel

        return ChoiceModel(owner)

    @Slot(str, result="QVariantList")
    def conversionPoints(self, key: Any) -> Any:
        from ..routing_choices import point_rows

        return point_rows(self.controller.session.document, key)

    @Slot(str, "QVariantMap", result="QVariantList")
    def routingChoices(self, key: Any, settings: Any) -> Any:
        return self.controller.routing_choices.rows(self.controller.session.document, key, settings)

    @Slot(str, "QVariantMap", result="QVariant")
    def createConstruction(self, operation: Any, arguments: Any) -> Any:
        return self.controller.creation_selection.create(operation, arguments)
