"""Qt adapter for the session issue API, with revision-gated incremental projection."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from . import issue_projection as projection
from .record_model import RecordModel

FIELDS = ("issueId", "summary", "severity", "targetLabel", "freshness", "dismissed", "code")


class IssuePanel(QObject):
    changed = Signal()
    pinReviewRequested = Signal(str)

    @Slot(str)
    def reviewPins(self, curve):
        self.pinReviewRequested.emit(curve)

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.model = RecordModel(self, FIELDS, "issueId")
        self.model.setObjectName("issueRows")
        self.selected, self.search = "", ""
        self.filters, self.show_dismissed, self.offset = {}, False, 0
        self._state, self._detail, self.signature = {}, {}, None
        self.label_cursor, self.label_revision = -1, 0

    @Property(QObject, constant=True)
    def issueModel(self):
        return self.model

    @Property("QVariantMap", notify=changed)
    def state(self):
        return self._state

    @Property("QVariantMap", notify=changed)
    def detail(self):
        return self._detail

    def synchronize(self):
        session = self.controller.session
        signature = self.context()
        if signature == self.signature:
            return
        if self.signature is not None and self.signature[0] is not session:
            self.selected, self.offset = "", 0
        self.signature = signature
        self.refresh()

    def context(self):
        session = self.controller.session
        return (
            session,
            session.issues.repository.revision,
            self.labels(),
            session.active_workspace,
            session.history.before is not None,
            session.waiting_save,
        )

    def labels(self):
        session = self.controller.session
        if self.signature is not None and self.signature[0] is not session:
            self.label_cursor = -1
        delta = session.changes.since(self.label_cursor)
        self.label_cursor = session.changes.serial
        values = (*delta.entities.values(), *delta.controls.values(), *delta.objects.values())
        if delta.reset or any({"name", "@membership"} & value for value in values):
            self.label_revision += 1
        return self.label_revision

    def refresh(self):
        values = projection.rows(self)
        self.offset = min(self.offset, max(0, ((len(values) - 1) // 100) * 100))
        self.model.synchronize_records(values[self.offset : self.offset + 100])
        self.update_summary(len(values))
        self._detail = projection.detail(self)
        self.changed.emit()

    def update_summary(self, total):
        session = self.controller.session
        status = session.issues.presentation.status()
        self._state = dict(
            count=status["issue_count"],
            summary=projection.status_text(status),
            complete=status["complete"],
            total=total,
            offset=self.offset,
            canNavigate=session.history.before is None and not session.waiting_save,
        )

    @Slot(str, str, bool)
    def filter(self, text, severity, dismissed):
        self.search, self.show_dismissed, self.offset = text, dismissed, 0
        self.filters = {"severity": severity} if severity else {}
        self.refresh()

    @Slot(int)
    def page(self, direction):
        self.offset = max(0, self.offset + direction * 100)
        self.refresh()

    @Slot(str)
    def selectIssue(self, identity):
        self.selected = identity
        self.refresh()
        if self._state.get("canNavigate") and self._detail.get("evidence", {}).get("witness"):
            self.controller.spatial_evidence.show(identity)

    @Slot()
    def showGeometry(self):
        self.controller.spatial_evidence.show(self.selected)

    @Slot(str, "QVariantMap")
    def run(self, operation, arguments):
        try:
            self.controller.session.command(operation, **arguments)
        except Exception as error:
            self.controller.message = str(error)
            self.controller.notify()
        self.refresh()

    @Slot(str, bool)
    def navigate(self, target, frame):
        if not self._state.get("canNavigate"):
            return
        if target in self.controller.session.document.registry.records:
            self.controller.select(target)
            if frame:
                self.controller.frameSelection()
