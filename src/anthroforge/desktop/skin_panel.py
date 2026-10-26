"""Small skin settings projection, separate from anatomy selection and computed payloads."""

from dataclasses import asdict

from PySide6.QtCore import Property, QObject, Signal


class SkinPanel(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.current = None
        self.display = ""
        self.values = {}
        controller.changed.connect(self.refresh)
        self.refresh()

    def refresh(self):
        skin = self.controller.session.document.skin
        display = self.controller.session.workspace.skin_display
        if skin is self.current and display == self.display:
            return
        self.current = skin
        self.display = display
        self.values = asdict(skin) | {"display": display}
        self.changed.emit()

    @Property(dict, notify=changed)
    def state(self):
        return self.values
