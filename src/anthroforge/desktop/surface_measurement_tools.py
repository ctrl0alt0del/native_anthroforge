"""View-local measurements follow accepted geometry without writing to the document."""

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from anthroforge.application import inspection_surfaces, tissue_inspection

from .volume_inspection_tools import VolumeInspectionTools


class SurfaceMeasurementTools(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.enabled, self.target, self.stage = controller, False, "", "final"
        self.report, self.context, self.receipt, self.error = {}, None, None, ""
        self.frozen = None
        self.input_cache = None
        self.volumes = VolumeInspectionTools(controller)
        self.volumes.changed.connect(self.changed)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(60)
        self.timer.timeout.connect(self.submit)

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            enabled=self.enabled,
            target=self.target,
            stage=self.stage,
            report=self.report,
            error=self.error,
        )

    @Property(QObject, constant=True)
    def volume(self):
        return self.volumes

    @Slot(result="QVariantMap")
    def snapshot(self):
        return dict(
            self.state,
            lines=self.report.get("lines", []),
            section=self.report.get("section", {}),
            volume=self.volumes.report.get("lines", []),
        )

    @Slot(str, str)
    def show(self, target, stage):
        self.enabled, self.target, self.stage = True, target, stage
        self.context = None
        self.frozen = None
        self.synchronize()

    @Slot()
    def cancel(self):
        self.timer.stop()
        tissue_inspection.cancel(self.controller.session, "measurements")
        self.enabled, self.report, self.context = False, {}, None
        self.changed.emit()

    def input_key(self):
        session, section = self.controller.session, self.controller.section_tools
        stamp = self.input_stamp(session, section)
        if self.input_cache and self.input_cache[0] == stamp:
            return self.input_cache[1]
        surface = inspection_surfaces.get(session, self.target, self.stage)
        plane = (
            tuple(section.plane) if section.enabled and section.target == surface.target else None
        )
        value = session, surface, plane
        self.input_cache = stamp, value
        return value

    def input_stamp(self, session, section):
        return (
            session,
            session.document,
            self.target,
            self.stage,
            section.target,
            tuple(section.plane),
            section.enabled,
        )

    def synchronize(self):
        self.volumes.synchronize()
        if not self.enabled:
            return
        try:
            key = self.input_key()
            if self.frozen == key:
                return
            if key != self.context:
                self.invalidate(key)
            self.receive()
        except (ValueError, KeyError) as error:
            self.fail(str(error))

    def fail(self, error):
        if self.report or self.error != error:
            self.report, self.error = {}, error
            self.changed.emit()

    def invalidate(self, key):
        tissue_inspection.cancel(self.controller.session, "measurements")
        self.context, self.report, self.error = key, {}, ""
        self.timer.start()
        self.changed.emit()

    def submit(self):
        if not self.enabled or self.context is None:
            return
        _, surface, plane = self.context
        options = dict(target=self.target, stage=self.stage, expected_asset=surface.asset)
        if plane is not None:
            options["plane"] = plane
        self.controller.run("geometry.measure", options)

    def receive(self):
        session = self.controller.session
        value = session.tissue_inspection.values.get("measurements")
        key = (value.job, value.state, id(value.asset), self.context) if value else None
        if key == self.receipt:
            return
        self.receipt = key
        status = tissue_inspection.status(session, "measurements")
        self.report = status.get("report", {}) if status["state"] == "ready" else {}
        self.error = status.get("error", "")
        self.changed.emit()

    def restore(self, report):
        surface = report["surface"]
        self.enabled, self.target, self.stage = True, surface["target"], surface["stage"]
        self.report, self.frozen = report, self.input_key()
        self.changed.emit()
