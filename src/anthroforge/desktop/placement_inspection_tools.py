"""An explicit click compares preview and confirmed placement without editing anatomy."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import binding_inspection, tissue_inspection
from anthroforge.application.inspection_context import scene_signature


class PlacementInspectionTools(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.active, self.report = controller, False, {}
        self.context, self.status, self.frozen = None, {}, None
        self.kind, self.binding_rows, self.selection_key = "placement", [], None

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(self.status, active=self.active, report=self.report, bindings=self.binding_rows)

    @Slot(result="QVariantMap")
    def snapshot(self):
        return dict(self.state, lines=self.report.get("lines", []))

    @Slot()
    def toggle(self):
        session = self.controller.session
        if session.history.before is not None or session.waiting_save:
            return
        if self.active:
            return self.cancel()
        self.controller.cancelViewportTools(self)
        self.active = True
        self.changed.emit()

    @Slot()
    def cancel(self):
        self.active = False
        self.changed.emit()

    @Slot()
    def clear(self):
        self.cancel()
        tissue_inspection.cancel(self.controller.session, self.kind)
        self.report, self.context, self.frozen = {}, None, None
        self.changed.emit()

    @Slot("QVariantList", "QVariantList", bool)
    def probe(self, origin, direction, confirm):
        targets = self.controller.snap_ids
        if not self.active or not confirm or not targets:
            return
        self.frozen = None
        self.kind = "placement"
        options = dict(
            target=self.controller.selection or targets[0],
            targets=targets,
            position=origin,
            direction=direction,
        )
        self.controller.run("geometry.placement", options)
        self.synchronize()

    def synchronize(self):
        session = self.controller.session
        self.update_bindings(session)
        if self.frozen is not None and self.frozen == scene_signature(session.document):
            return
        value = session.tissue_inspection.values.get(self.kind)
        context = (
            (session, session.document.revision, value.job, value.state, id(value.asset))
            if value
            else None
        )
        if context == self.context:
            return
        self.context = context
        self.receive(session)

    def receive(self, session):
        status = tissue_inspection.status(session, self.kind)
        self.status = {k: v for k, v in status.items() if k != "report"}
        self.report = status.get("report", {}) if status["state"] == "ready" else {}
        self.changed.emit()

    def update_bindings(self, session):
        target = self.controller.selection
        key = (session, target, session.document.registry.records.get(target))
        if key != self.selection_key:
            self.selection_key = key
            self.binding_rows = binding_inspection.bindings(session, target)
            self.changed.emit()

    @Slot(str)
    def inspectBinding(self, point):
        self.kind, self.frozen, self.context = "binding", None, None
        self.controller.run("geometry.binding", dict(target=self.controller.selection, point=point))
        self.synchronize()

    def restore(self, report):
        self.report, self.active = report, False
        self.frozen = scene_signature(self.controller.session.document)
        self.changed.emit()
