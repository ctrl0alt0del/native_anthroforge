"""Per-view optional route evidence; ordinary solver and accepted paths stay untouched."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import tissue_inspection as inspection

from . import route_inspection_view as view


class RouteInspectionTools(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.stamp, self.report = controller, None, {}
        self.index, self.status, self.visible = 0, dict(state="idle"), False
        self.show_contacts, self.paths, self.contacts, self.labels = True, [], [], []
        self.frozen_context = None

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            self.status,
            visible=self.visible,
            index=self.index,
            labels=self.labels,
            showContacts=self.show_contacts,
            details=view.details(self),
            omitted=self.report.get("omitted", 0),
        )

    @Slot(bool)
    def start(self, cold):
        result = self.controller.run(
            "curve.inspect.route", dict(target=self.controller.selection, cold=cold)
        )
        if result:
            self.visible, self.report = True, {}
            self.synchronize()

    @Slot(result="QVariantMap")
    def snapshot(self):
        return dict(self.state, paths=self.paths, contacts=self.contacts)

    def synchronize(self):
        session = self.controller.session
        if self.frozen_context == (id(session.document), self.controller.selection):
            return
        self.update_status(session)

    def update_status(self, session):
        self.frozen_context = None
        value = session.tissue_inspection.values.get("route")
        stamp = (
            id(session.document),
            self.controller.selection,
            value.job if value else "",
            value.state if value else "",
            id(value.asset) if value else 0,
            session.preferences.value.routing_backend,
        )
        if stamp == self.stamp:
            return
        self.stamp = stamp
        self.read_status(session)

    def read_status(self, session):
        status = inspection.status(session, "route")
        self.status = {k: v for k, v in status.items() if k != "report"}
        self.report = status.get("report", {}) if status["state"] == "ready" else {}
        self.labels = [view.label(row) for row in self.report.get("records", [])]
        self.index = max(0, len(self.labels) - 1)
        self.refresh()

    def refresh(self):
        current = self.visible and self.report.get("target") == self.controller.selection
        self.paths, self.contacts = view.lines(self) if current else ([], [])
        self.changed.emit()

    @Slot(int)
    def select(self, index):
        self.index = max(0, min(index, len(self.labels) - 1))
        self.refresh()

    @Slot(bool)
    def setContacts(self, enabled):
        self.show_contacts = enabled
        self.refresh()

    @Slot()
    def hide(self):
        self.visible = False
        self.frozen_context = None
        inspection.cancel(self.controller.session, "route")
        self.synchronize()

    def restore(self, snapshot):
        if not snapshot:
            return
        self.report, self.visible = snapshot["report"], True
        self.status = dict(state="ready", target=self.report["target"])
        self.labels = [view.label(row) for row in self.report.get("records", [])]
        self.index, self.show_contacts = snapshot["index"], snapshot["contacts"]
        self.frozen_context = (id(self.controller.session.document), self.controller.selection)
        self.refresh()
