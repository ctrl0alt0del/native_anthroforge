"""Reconstruction navigation invokes the same scoped operations as headless clients."""

import json

from PySide6.QtCore import Property, QObject, Signal, Slot


class ReconstructionPanel(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self._open, self._floating = False, False
        self._signature, self._data = None, "{}"

    @Property(str, notify=changed)
    def dataJson(self):
        return self._data

    @Property(bool, notify=changed)
    def opened(self):
        return self._open

    @Property(bool, notify=changed)
    def floating(self):
        return self._floating

    @Slot(bool)
    def setOpen(self, value):
        self._open = value
        self.synchronize()
        self.changed.emit()

    @Slot(bool)
    def setFloating(self, value):
        self._floating = value
        self.changed.emit()

    def synchronize(self):
        session = self.controller.session
        root = session.contexts.scene("")
        signature = (id(root.reconstruction), session.contexts.visible)
        if signature == self._signature:
            return
        self._signature = signature
        self._data = json.dumps(session.command("variant.inspect"))
        self.changed.emit()

    @Slot()
    def create(self):
        session = self.controller.session
        subjects = [
            key
            for key in self.controller.selectedObjects
            if key in session.document.registry.anatomy
        ]
        self.run("variant.create", dict(subjects=subjects))

    @Slot(str, "QVariantMap", result="QVariant")
    def run(self, operation, arguments):
        controller = self.controller
        before = controller.session.contexts.visible
        result = controller.run(operation, arguments)
        if before != controller.session.contexts.visible:
            controller.authoring.setEditing(False)
            controller.drawing_tools.cancel()
            controller.refresh()
        self._signature = None
        self.synchronize()
        return result
