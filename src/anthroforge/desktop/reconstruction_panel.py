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
        self._page = "Variants"

    @Property(str, notify=changed)
    def page(self):
        return self._page

    @Slot(str)
    def setPage(self, page):
        self._page, self._signature = page, None
        self.synchronize()

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
        signature = (id(root.reconstruction), session.contexts.visible, self._page)
        if self._page == "Reviews":
            signature += (id(session.document), id(root))
        if signature == self._signature:
            return
        self._signature = signature
        self._data = json.dumps(self.projection())
        self.changed.emit()

    def projection(self):
        session = self.controller.session
        result = session.command("variant.inspect")
        commands = {
            "Catalogue": "catalogue.inspect",
            "Reviews": "review.inspect",
            "Queue": "reconstruction.queue.inspect",
        }
        if self._page in commands:
            result["detail"] = session.command(commands[self._page])
        return result

    @Slot(str, str)
    def assignSelection(self, type_id, side):
        self.run(
            "catalogue.assign_many",
            dict(
                targets=self.controller.selectedObjects,
                type_id=type_id,
                side=side,
                variant=self.controller.session.contexts.visible,
            ),
        )

    @Slot("QVariantList")
    def selectMembers(self, identities):
        session = self.controller.session
        selected = [key for key in identities if key in session.document.registry.records]
        self.controller.selectObjects(selected)

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
