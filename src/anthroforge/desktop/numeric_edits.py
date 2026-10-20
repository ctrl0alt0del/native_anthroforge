"""Own a numeric scrub's application transaction, including interrupted gestures."""

from PySide6.QtCore import Property, QObject, Signal, Slot
from shiboken6 import isValid


class NumericEdits(QObject):
    changed = Signal()
    finished = Signal(bool)

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.owner = controller, None

    @Property(bool, notify=changed)
    def active(self):
        return self.owner is not None

    @Slot(QObject, result=bool)
    def begin(self, owner):
        session = self.controller.session
        if self.active or session.history.before is not None or session.waiting_save:
            return False
        session.begin()
        self.owner = owner
        owner.destroyed.connect(self.cancel)
        self.changed.emit()
        return True

    @Slot(QObject)
    def commit(self, owner):
        if owner is self.owner:
            self.finish(False)

    @Slot()
    def cancel(self):
        if self.active:
            self.finish(True)

    def finish(self, canceled):
        owner = self.owner
        self.owner = None
        if isValid(owner):
            owner.destroyed.disconnect(self.cancel)
        self.controller.run("cancel" if canceled else "commit", {})
        self.finished.emit(canceled)
        self.changed.emit()
