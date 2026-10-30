"""RuntimeView owns its QML-facing interaction and presentation contract."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from .. import presentation
from ..property_projection import PropertyProjection

if TYPE_CHECKING:
    from ..controller import Controller


class RuntimeView(QObject):
    metricsChanged = Signal()

    def __init__(self, controller: Controller) -> None:
        super().__init__(controller)
        self.controller = controller
        self._state = PropertyProjection(self)
        self._metrics: dict[str, Any] = {}

    @Property(QObject, constant=True)
    def state(self) -> Any:
        return self._state

    @Property("QVariantMap", notify=metricsChanged)
    def metrics(self) -> Any:
        return self._metrics

    @Slot(str, "QVariantMap", result="QVariant")
    def run(self, operation: str, arguments: dict[str, Any]) -> Any:
        return self.controller.run(operation, arguments)

    def synchronize(self) -> None:
        self._state.synchronize(self.snapshot())

    def refresh_metrics(self):
        metrics = self.controller.session.scheduler.metrics.report()
        if metrics != self._metrics:
            self._metrics = metrics
            self.metricsChanged.emit()

    def snapshot(self):
        return {
            **self.view_state(),
            "message": self.controller.message,
            "revision": self.controller.session.document.revision,
            "dirty": self.controller.session.saved_revision != self.controller.session.serial,
            "blocked": self.controller.session.scheduler.blocked,
            "waiting": self.controller.session.waiting_save,
            "publishing": sum(len(m.pending) for m in self.controller.geometry_models()),
            "path": str(self.controller.session.path or ""),
        }

    def view_state(self):
        return {
            **presentation.state(self.controller),
            "attachments": self.controller.session.document.attachments_enabled,
            "mode": self.controller.session.document.update_mode,
            "workspaces": [w.name for w in self.controller.session.document.workspaces],
            "workspace": self.controller.session.active_workspace,
            "hidden": list(self.controller.session.workspace.hidden),
            "unpickable": list(self.controller.session.workspace.unpickable),
            "handles": self.controller.session.workspace.handles,
            "anchors": self.controller.session.workspace.anchors,
            "diagnostics": self.controller.session.workspace.diagnostics,
        }
