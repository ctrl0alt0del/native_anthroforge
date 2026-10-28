"""One review window over the shared whole-skeleton preparation operations."""

import json

from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot

from . import skeleton_projection
from .skeleton_scene import SkeletonScene


class SkeletonPanel(QObject):
    changed = Signal()
    requested = Signal()
    finished = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.scene = SkeletonScene(controller, self)
        self.scene.selected.connect(self.selectObject)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(180)
        self.timer.timeout.connect(self.prepare)
        self.reset()

    def reset(self):
        self.active, self.signature = False, None
        self.matches, self.options, self.approved = {}, {}, set()
        self._state, self._references, self._targets, self._properties = {}, [], [], []
        self.focus, self.target, self._selection = "", {}, ""
        self.initialized = False

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            self._state,
            matches=self.matches,
            options=self.options,
            approved=sorted(self.approved),
            reference=self.focus,
            target=self.target,
            selection=self._selection,
            parents=skeleton_projection.parents(self),
        )

    @Property(QObject, constant=True)
    def comparison(self):
        return self.scene

    @Property("QVariantList", notify=changed)
    def references(self):
        return self._references

    @Property("QVariantList", notify=changed)
    def targets(self):
        return self._targets

    @Property("QVariantList", notify=changed)
    def properties(self):
        return self._properties

    @Slot(str)
    def inspect(self, url):
        self.cancel()
        self.reset()
        self.active = True
        path = QUrl(url).toLocalFile() if QUrl(url).isLocalFile() else url
        self.controller.run("skeleton_update.inspect", dict(path=path))
        self.synchronize()
        self.requested.emit()

    @Slot(str, str)
    def match(self, source, destination):
        self.matches.pop(source, None)
        self.options.setdefault("additions", {}).pop(source, None)
        if destination:
            self.matches[source] = destination
        self.queue()

    @Slot(str, str)
    def add(self, source, parent):
        self.matches.pop(source, None)
        self.options.setdefault("additions", {})[source] = parent
        self.queue()

    @Slot(str, "QVariant")
    def option(self, name, value):
        self.options[name] = value
        self.queue()

    @Slot(str, str, "QVariant")
    def decision(self, group, key, value):
        if group in ("disable_formulas", "use_formula_values", "remove_shortcuts"):
            entries = set(self.options.get(group, ()))
            entries.add(key) if value else entries.discard(key)
            self.options[group] = sorted(entries)
        else:
            self.options.setdefault(group, {})[key] = value
        self.queue()

    @Slot(str, bool)
    def acknowledge(self, key, value):
        self.approved.add(key) if value else self.approved.discard(key)
        self.changed.emit()

    def queue(self):
        self.approved.clear()
        self._state = dict(self._state, ready=False, state="preparing", error="")
        self.timer.start()
        self.changed.emit()

    @Slot()
    def prepare(self):
        runtime = self.controller.session.skeleton_update.runtime
        if runtime.source.state == "ready" and (self.matches or self.options.get("additions")):
            self.controller.run(
                "skeleton_update.prepare",
                dict(source=runtime.source.token, matches=self.matches, **self.options),
            )
        else:
            runtime.cancel_preparation()
        self.signature = None
        self.synchronize()

    def synchronize(self):
        if not self.active or self.timer.isActive():
            return
        runtime = self.controller.session.skeleton_update.runtime
        stamp = self.stamp(runtime)
        if stamp == self.signature:
            return
        self.signature = stamp
        self._state = json.loads(json.dumps(self.controller.session.skeleton_update.status()))
        if self._state.get("state") == "stale":
            self.queue()
            return
        skeleton_projection.synchronize(self)
        self.scene.synchronize(runtime.preparation.candidate)
        self.changed.emit()

    def stamp(self, runtime):
        return (
            runtime.source.token,
            runtime.source.state,
            runtime.preparation.token,
            runtime.preparation.state,
            id(self.controller.session.document),
        )

    @Slot(str)
    def select(self, key):
        self._selection = key
        self.scene.focus(key)
        self.changed.emit()

    @Slot(str)
    def selectObject(self, key):
        self._selection = key
        self.changed.emit()

    @Slot(str, str, result="QVariantList")
    def propertyChoices(self, key, target):
        return skeleton_projection.control_properties(self, key, target)

    @Slot(str, "QVariantMap", "QVariantList")
    def correctPlacement(self, owner, point, position):
        rows = self.options.setdefault("placements", {}).setdefault(owner, {})
        rows[point["point"]] = dict(
            position=list(position),
            target=point["target"],
            role=point["role"],
            instance=point.get("instance", ""),
        )
        self.options.setdefault("rebind", {})["rebind:" + owner + ":" + point["target"]] = True
        self.queue()

    @Slot(str, str)
    def resetPlacement(self, owner, point):
        rows = self.options.setdefault("placements", {}).get(owner, {})
        rows.pop(point, None)
        self.queue()

    @Slot(str)
    def selectReference(self, key):
        self.focus, self.target = key, {}
        self._targets, self._properties = skeleton_projection.targets(self), []
        self.changed.emit()

    def current(self):
        return next((r for r in self._references if r["key"] == self.focus), {})

    @Slot("QVariantMap")
    def selectTarget(self, target):
        self.target = dict(target)
        self._properties = skeleton_projection.properties(self)
        if not self.current().get("property"):
            self.mapTarget({})
        self.changed.emit()

    @Slot("QVariantMap")
    def mapTarget(self, prop):
        value = dict(
            action="map", target=self.target["target"], instance=self.target.get("instance", "")
        )
        if prop:
            value["property"] = dict(prop)
        self.decision("mappings", self.focus, value)

    @Slot(str)
    def action(self, action):
        value = dict(self.options.get("mappings", {}).get(self.focus, {}))
        if action == "rebind":
            value["rebind"] = not value.get("rebind", False)
        else:
            value = dict(action=action)
        self.decision("mappings", self.focus, value)

    @Slot()
    def apply(self):
        result = self.controller.run(
            "skeleton_update.apply",
            dict(token=self._state.get("token", ""), approved=sorted(self.approved)),
        )
        if result:
            self.finished.emit()
            self.cancel()

    @Slot()
    def cancel(self):
        self.timer.stop()
        if self.active:
            self.controller.session.skeleton_update.cancel()
        self.active = False
        self.scene.synchronize(None)
