"""Opt-in, revision-gated details projection over the read-only application API."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from .property_projection import PropertyProjection


class InspectionPanel(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.enabled, self.signature = controller, False, None
        self.projection = PropertyProjection(self)

    @Property(QObject, constant=True)
    def detail(self):
        return self.projection

    @Slot(bool)
    def activate(self, enabled):
        self.enabled = enabled
        self.synchronize()

    def synchronize(self):
        if not self.enabled:
            return
        owner = self.controller
        signature = self.context()
        if signature == self.signature:
            return
        self.signature = signature
        result = (
            owner.session.command("inspect.target", entity=owner.selection)
            if owner.selection
            else {}
        )
        self.projection.synchronize(result)

    def context(self):
        owner = self.controller
        return (
            owner.session,
            owner.session.document.revision,
            owner.selection,
            owner.session.active_workspace,
        )

    @Slot(str, bool)
    def navigate(self, target, frame):
        owner = self.controller
        if owner.session.history.before is not None or owner.session.waiting_save:
            return
        owner.select(target)
        if frame:
            owner.frameSelection()
