"""Session comparison presentation; view modes never mutate authored anatomy."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import shortcut_comparison

from . import comparison_images, shortcut_comparison_scene
from .models import RenderModel
from .render_layer import RenderLayer
from .values import qml


class ShortcutComparisonView(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.mode = controller, "After"
        self.model = RenderModel(self)
        self.images = RenderModel(self)
        self.layers = {name: RenderLayer(self.images, name) for name in ("NORMAL", "FRONT", "BACK")}
        self.stamp, self.value = None, shortcut_comparison.inspect(controller.session)
        self.points = []
        self.baseline_id, self.events = "", 0

    @Property(QObject, constant=True)
    def geometry(self):
        return self.model

    @Slot(str, result=QObject)
    def imageLayer(self, name):
        return self.layers[name]

    @Property("QVariantMap", notify=changed)
    def state(self):
        return qml(dict(self.value, mode=self.mode, points=self.points))

    @Property(bool, notify=changed)
    def before(self):
        return self.mode == "Before" and bool(self.value.get("active"))

    @Slot(str)
    def capture(self, shortcut):
        self.controller.run("shortcut.comparison.capture", dict(shortcut=shortcut))
        self.synchronize()

    @Slot()
    def clear(self):
        self.controller.run("shortcut.comparison.clear", {})
        self.synchronize()

    @Slot(str)
    def setMode(self, mode):
        if mode not in ("Before", "After", "Overlay"):
            return
        self.mode = mode
        self.synchronize()
        self.changed.emit()

    def editing(self, operation):
        if self.before and operation in ("shortcut.set", "driver.value", "begin"):
            self.setMode("After")

    def synchronize(self):
        session = self.controller.session
        state = session.shortcut_comparison
        value = shortcut_comparison.inspect(session)
        self.observe(value)
        self.stage(state.baseline, session.workspace)
        if value != self.value:
            self.value = value
            self.changed.emit()

    def observe(self, value):
        if value["id"] != self.baseline_id:
            self.baseline_id, self.events, self.mode = value["id"], 0, "After"
        events = value["replay"]["events"]
        journal = self.controller.session.shortcut_comparison.journal.events
        edits = any(
            e["operation"] in ("begin", "driver.value", "shortcut.set")
            for e in journal[self.events :]
        )
        if self.mode == "Before" and edits:
            self.mode = "After"
            self.changed.emit()
        self.events = events

    def stage(self, baseline, workspace):
        active = baseline is not None and self.mode != "After"
        stamp = (baseline.id if active else "", workspace)
        if stamp == self.stamp:
            return
        self.stamp = stamp
        rows, leases = shortcut_comparison_scene.rows(baseline, workspace) if active else ([], [])
        self.model.publish(rows, leases)
        self.points = shortcut_comparison_scene.points(baseline, workspace) if active else []
        self.stage_images(baseline, workspace, active)
        self.changed.emit()

    def stage_images(self, baseline, workspace, active):
        rows, leases = comparison_images.rows(baseline, workspace) if active else ([], [])
        self.images.publish(rows, leases)

    @Slot()
    def compare(self):
        self.controller.run("shortcut.comparison.inspect", dict(refresh=True))
        self.synchronize()
