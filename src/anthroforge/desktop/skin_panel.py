"""Small skin settings projection, separate from anatomy selection and computed payloads."""

from dataclasses import asdict

from PySide6.QtCore import Property, QObject, Signal

from . import skin_contributor
from .skin_fit_panel import SkinFitPanel


class SkinPanel(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.current = None
        self.display = None
        self.values = {}
        self.fitting = SkinFitPanel(controller)
        controller.changed.connect(self.refresh)
        controller.selectionChanged.connect(self.refresh)
        self.unsubscribe = controller.session.skin_status.subscribe(self.changed.emit)
        self.refresh()

    def refresh(self):
        skin = self.controller.session.document.skin
        session = self.controller.session
        display = context(self.controller, session)
        if skin is self.current and display == self.display:
            return
        self.current = skin
        self.display = display
        self.values = asdict(skin) | dict(
            display=display[0], contributor=skin_contributor.describe(session, display[1])
        )
        self.changed.emit()

    @Property(dict, notify=changed)
    def state(self):
        return self.values

    @Property(dict, notify=changed)
    def readiness(self):
        return self.controller.session.skin_status.describe()["operations"]

    @Property(QObject, constant=True)
    def fits(self):
        return self.fitting


def context(controller, session):
    selected = getattr(getattr(controller, "object_selection", None), "primary", "")
    item = session.document.registry.records.get(selected)
    return session.workspace.skin_display, selected, session.workspace, id(item)
