"""View-local section controls; contours share the inspection job lifecycle."""

from math import isfinite

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from anthroforge.application import inspection_surfaces
from anthroforge.application import tissue_inspection as inspection
from anthroforge.application.inspection_context import scene_signature
from anthroforge.native import scene

from . import section_queries
from .tissue_inspection_tools import displayed_stage


class SectionTools(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.enabled, self.target = controller, False, ""
        self.axis, self.position, self.flip, self.cut, self.whole_scene = 0, 0.0, False, True, False
        self.reports, self.error, self.context, self.requested = [], "", None, None
        self.pick_cache = []
        self.receipt = None
        self.stage, self.selection = "final", ""
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(60)
        self.timer.timeout.connect(self.submit)

    @property
    def plane(self):
        normal = [int(self.axis == i) * (-1 if self.flip else 1) for i in range(3)]
        return [*normal, self.position if self.flip else -self.position]

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            enabled=self.enabled,
            target=self.target,
            axis=self.axis,
            position=self.position,
            flip=self.flip,
            cut=self.cut,
            wholeScene=self.whole_scene,
            plane=self.plane,
            error=self.error,
        )

    def applies(self, owner):
        return self.enabled and self.cut and (self.whole_scene or owner == self.target)

    @Slot(result="QVariantMap")
    def snapshot(self):
        return dict(self.state, contours=self.reports)

    def planes(self, owners):
        for previous, planes in self.pick_cache:
            if previous is owners:
                return planes
        value = [self.plane if self.applies(key) else [0, 0, 0, 0] for key in owners]
        self.pick_cache = [(owners, value), *self.pick_cache[:1]]
        return value

    @Slot(bool)
    def enable(self, enabled):
        if not enabled:
            return self.cancel()
        self.attempt(self.start)

    def start(self):
        controller = self.controller
        controller.authoring.setEditing(False)
        controller.cancelViewportTools()
        tool = controller.tissue_inspection
        stage = (
            tool.stage or displayed_stage(controller.session, controller.selection)
            if controller.selectedData.get("is_tissue")
            else "final"
        )
        self.start_surface(controller.selection, stage)

    @Slot(str, str)
    def inspect(self, target, stage):
        self.attempt(lambda: self.start_surface(target, stage))

    def start_surface(self, target, stage):
        surface = inspection_surfaces.get(self.controller.session, target, stage)
        surface.mesh(self.controller.session)
        self.target, self.stage, self.selection = (
            surface.target,
            surface.stage,
            self.controller.selection,
        )
        self.enabled = True
        self.center()
        self.synchronize()
        self.changed.emit()

    @Slot()
    def cancel(self):
        self.enabled, self.reports, self.requested = False, [], None
        self.pick_cache = []
        self.timer.stop()
        inspection.cancel(self.controller.session, "section")
        self.changed.emit()

    @Slot()
    def center(self):
        session = self.controller.session
        surface = inspection_surfaces.get(session, self.target, self.stage)
        bounds = scene.bounds(session.engine, [surface.mesh(session).handle], [surface.frame])
        self.position = (bounds[self.axis] + bounds[3 + self.axis]) * 0.5
        self.invalidate()

    @Slot(str, "QVariant")
    def setting(self, name, value):
        if name == "axis" and int(value) in range(3):
            self.axis = int(value)
            self.center()
        elif name == "position" and isfinite(float(value)):
            self.position = float(value)
        elif name in ("flip", "cut", "whole_scene"):
            setattr(self, name, bool(value))
        self.invalidate()

    def invalidate(self):
        self.reports, self.pick_cache, self.requested = [], [], None
        self.receipt = None
        self.timer.start()
        self.changed.emit()

    def synchronize(self):
        if not self.enabled:
            return
        if self.controller.selection != self.selection or self.controller.authoring.editing:
            return self.cancel()
        context = (
            scene_signature(self.controller.session.document),
            id(self.controller.tissue_inspection.model.displayed),
            self.plane,
        )
        if context != self.context:
            self.context = context
            self.invalidate()
        self.receive()

    def submit(self):
        self.attempt(self.request)

    def request(self):
        surfaces = section_queries.displayed(self)
        if not self.enabled or not surfaces:
            return
        self.requested = list(self.plane)
        inspection.start(
            self.controller.session,
            "section",
            self.target,
            stage=self.stage,
            plane=self.plane,
            surfaces=surfaces,
        )

    def receive(self):
        value = self.controller.session.tissue_inspection.values.get("section")
        stamp = (
            (id(self.controller.session.document), value.job, value.state, id(value.asset))
            if value
            else None
        )
        if stamp == self.receipt:
            return
        self.receipt = stamp
        self.update_report()

    def update_report(self):
        status = inspection.status(self.controller.session, "section")
        report = status.get("report", {})
        rows = (
            report.get("surfaces", [])
            if status["state"] == "ready" and report.get("plane") == self.plane
            else []
        )
        error = status.get("error", "")
        if rows != self.reports or error != self.error:
            self.reports, self.error = rows, error
            self.changed.emit()

    def attempt(self, action):
        try:
            action()
        except (ValueError, KeyError) as error:
            self.error = str(error)
            self.changed.emit()
