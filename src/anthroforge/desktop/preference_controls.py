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
        self.set_preference(routing_backend=value)

    @Slot(str)
    def setRoutingConversionPoints(self, value):
        self.set_preference(routing_conversion_points=value)

    @Slot(str)
    def setFiberPropagation(self, value):
        self.set_preference(fiber_propagation=value)

    @Slot(bool)
    def setAutosaveEnabled(self, value):
        self.set_preference(autosave_enabled=value)

    @Slot(int)
    def setAutosaveMinutes(self, value):
        self.set_preference(autosave_minutes=value)

    def set_preference(self, **values):
        try:
            self.controller.session.command("preferences.set", **values)
            self.error = ""
        except (OSError, ValueError) as error:
            self.error = str(error)
        self.changed.emit()

    @Slot()
    def refresh(self):
        self.changed.emit()
