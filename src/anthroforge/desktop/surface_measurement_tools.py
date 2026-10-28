"""View-local measurements follow accepted geometry without writing to the document."""

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from anthroforge.application import inspection_surfaces, tissue_inspection


class SurfaceMeasurementTools(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.enabled, self.target, self.stage = controller, False, "", "final"
        self.report, self.context, self.receipt, self.error = {}, None, None, ""
        self.frozen = None
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

    @Slot(result="QVariantMap")
    def snapshot(self):
        return dict(
            self.state, lines=self.report.get("lines", []), section=self.report.get("section", {})
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
        surface = inspection_surfaces.get(session, self.target, self.stage)
        plane = (
            tuple(section.plane) if section.enabled and section.target == surface.target else None
        )
        return session, surface, plane

    def synchronize(self):
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
            self.report, self.error = {}, str(error)
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
