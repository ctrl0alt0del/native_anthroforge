"""Explicit volume comparisons use the existing read-only inspection lifecycle."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import tissue_inspection


class VolumeInspectionTools(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.report, self.status = controller, {}, {}
        self.receipt, self.frozen = None, None

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(self.status, report=self.report)

    @Slot(str, str, str, str)
    def compare(self, target, stage, other, role):
        self.frozen = None
        other_stage = "base" if role == "TISSUE_BASE" else "final"
        self.controller.run(
            "geometry.volume",
            dict(target=target, stage=stage, other=other, other_stage=other_stage),
        )
        self.synchronize()

    @Slot()
    def clear(self):
        tissue_inspection.cancel(self.controller.session, "volume")
        self.report, self.status, self.frozen, self.receipt = {}, {}, None, None
        self.changed.emit()

    def synchronize(self):
        session = self.controller.session
        if self.frozen is session.document:
            return
        value = session.tissue_inspection.values.get("volume")
        state = (value.job, value.state, id(value.asset)) if value else None
        stamp = session, session.document, state
        if stamp == self.receipt:
            return
        self.receipt = stamp
        self.status = tissue_inspection.status(session, "volume")
        self.report = self.status.pop("report", {}) if self.status["state"] == "ready" else {}
        self.changed.emit()

    def restore(self, report):
        self.report, self.frozen = report, self.controller.session.document
        self.changed.emit()
