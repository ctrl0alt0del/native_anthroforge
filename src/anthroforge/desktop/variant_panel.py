"""Variant reconciliation shares staged comparison and attachment review presentation."""

import json

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from . import skeleton_projection
from .skeleton_scene import SkeletonScene


class VariantPanel(QObject):
    changed = Signal()
    requested = Signal()
    finished = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.active, self.signature = controller, False, None
        self.variant, self.mode, self.selection = "", "promote", ""
        self.options, self.approved, self._state, self._review = {}, set(), {}, "{}"
        self.scene = SkeletonScene(controller, self)
        self.scene.selected.connect(self.select)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(180)
        self.timer.timeout.connect(self.prepare)

    @Property(QObject, constant=True)
    def comparison(self):
        return self.scene

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            skeleton_projection.summary(self._state),
            options=self.options,
            approved=sorted(self.approved),
            selection=self.selection,
            mode=self.mode,
        )

    @Property(str, notify=changed)
    def reviewJson(self):
        return self._review

    @Slot(str, str)
    def inspect(self, variant, mode):
        self.cancel()
        self.variant, self.mode, self.active = variant, mode, True
        self.options, self.approved, self.signature = {}, set(), None
        self.prepare()
        self.requested.emit()

    @Slot()
    def prepare(self):
        self.controller.run(
            "variant.review.prepare", dict(variant=self.variant, mode=self.mode, **self.options)
        )
        self.signature = None
        self.synchronize()

    def synchronize(self):
        if not self.active or self.timer.isActive():
            return
        session = self.controller.session
        value = session.variant_review.runtime.preparation
        stamp = (value.token, value.state, id(session.contexts.scene("")), id(session.document))
        if stamp == self.signature:
            return
        self.signature = stamp
        self._state = session.variant_review.status()
        affected, attachments = skeleton_projection.review(self._state)
        self._review = json.dumps(dict(affected=affected, attachments=attachments))
        self.scene.synchronize(value.candidate)
        self.changed.emit()

    @Slot(str, "QVariant")
    def option(self, name, value):
        self.options[name] = value
        self.queue()

    @Slot(str, str, "QVariant")
    def decision(self, group, key, value):
        self.options.setdefault(group, {})[key] = value
        self.queue()

    def queue(self):
        self.approved.clear()
        self._state = dict(self._state, ready=False, state="preparing")
        self.timer.start()
        self.changed.emit()

    @Slot(str, bool)
    def acknowledge(self, key, value):
        self.approved.add(key) if value else self.approved.discard(key)
        self.changed.emit()

    @Slot(str)
    def select(self, key):
        self.selection = key
        self.scene.focus(key)
        self.changed.emit()

    @Slot(str, "QVariantMap", "QVariantList")
    def correctPlacement(self, owner, point, position):
        rows = self.options.setdefault("placements", {}).setdefault(owner, {})
        rows[point["point"]] = dict(
            position=list(position),
            target=point["target"],
            role=point["role"],
            instance=point.get("instance", ""),
        )
        self.queue()

    @Slot(str, str)
    def resetPlacement(self, owner, point):
        self.options.setdefault("placements", {}).get(owner, {}).pop(point, None)
        self.queue()

    @Slot()
    def apply(self):
        result = self.controller.run(
            "variant.review.apply",
            dict(token=self._state.get("token", ""), approved=sorted(self.approved)),
        )
        if result is not None:
            if self.mode == "promote":
                self.controller.reconstruction_panel.run("variant.leave", {})
            self.cancel()
            self.finished.emit()

    @Slot()
    def cancel(self):
        self.timer.stop()
        self.controller.session.variant_review.cancel()
        self.active, self.signature = False, None
        self.scene.synchronize(None)
