"""Direct preference editing; no document refresh, transaction or job scheduling."""

from PySide6.QtCore import Property, QObject, Signal, Slot


class PreferenceControls(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.error = controller, ""

    @Property("QVariantMap", notify=changed)
    def state(self):
        value = self.controller.session.command("preferences.get")
        return dict(value, error=self.error or value["error"])

    @Slot(str)
    def setBackend(self, value):
        try:
            self.controller.session.command("preferences.set", routing_backend=value)
            self.error = ""
        except (OSError, ValueError) as error:
            self.error = str(error)
        self.changed.emit()

    @Slot()
    def refresh(self):
        self.changed.emit()
