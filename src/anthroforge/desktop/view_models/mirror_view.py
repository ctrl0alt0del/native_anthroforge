"""MirrorView owns its QML-facing interaction and presentation contract."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, Slot

if TYPE_CHECKING:
    from ..controller import Controller


class MirrorView(QObject):
    def __init__(self, controller: Controller) -> None:
        super().__init__(controller)
        self.controller = controller

    @Slot(str, result="QVariantList")
    def mirrorBindings(self, target: Any) -> Any:
        return (
            self.controller.session.command("mirror.attachment.inspect", target=target)
            if target
            else []
        )

    @Slot(result="QVariantList")
    def mirrorPlanes(self) -> Any:
        return self.controller.session.command("mirror.planes")

    @Slot(str, result="QVariantMap")
    def defaultMirrorPlane(self, source: Any) -> Any:
        if not source:
            return dict(axis="X", shift=0)
        values = self.controller.session.command("mirror.list", source=source)
        return dict(rule=values[0]["rule"]) if len(values) == 1 else dict(axis="X", shift=0)

    @Slot(str, str, result=bool)
    def mirrorTargetShared(self, source: Any, binding: Any) -> Any:
        return self.controller.session.command(
            "mirror.attachment.shared", source=source, binding=binding
        )
