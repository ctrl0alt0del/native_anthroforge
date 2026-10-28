"""Shared desktop review lifecycle; producers own source selection and application policies."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import replacement_assessments, replacement_status


class ReplacementPanel(QObject):
    changed = Signal()
    selectionRequested = Signal()
    reviewRequested = Signal()
    finished = Signal()

    def __init__(self, controller, slot, prefix, heading):
        super().__init__(controller)
        self.controller, self.slot, self.prefix = controller, slot, prefix
        self.target, self.shown, self._heading = "", "", heading
        self.active, self.signature = False, None
        self._state, self.arguments = {}, {}
        self._eligibility, self._eligibility_key, self._eligibility_document = {}, None, None

    @Property("QVariantMap", notify=changed)
    def state(self):
        return self._state

    @Property(str, constant=True)
    def heading(self):
        return self._heading

    @Property("QVariantMap", notify=changed)
    def eligibility(self):
        return self._eligibility

    @Slot(str)
    def choose(self, target):
        status = replacement_status.assess(self.controller.session, self.slot, target)
        if not status.available:
            self.controller.message = status.reason
            self.controller.notify()
            return
        if self.active:
            self.cancel()
        self.target = target
        self.selectionRequested.emit()

    def begin(self, arguments):
        self.arguments = arguments
        result = self.controller.run(self.prefix + ".assess", arguments)
        self.active = bool(result) and result.get("state") != "unchanged"
        self.signature = None
        self.synchronize()

    @Slot()
    def retry(self):
        self.begin(self.arguments)

    def synchronize(self):
        self.synchronize_eligibility()
        self.synchronize_review()

    def synchronize_eligibility(self):
        session = self.controller.session
        key = self.eligibility_key()
        if key == self._eligibility_key:
            return
        self._eligibility_key, self._eligibility_document = key, session.document
        status = replacement_status.describe(session, self.slot, self.controller.selectedId)
        if status != self._eligibility:
            self._eligibility = status
            self.changed.emit()

    def eligibility_key(self):
        session = self.controller.session
        value = getattr(session, self.slot)
        context = (
            session.active_workspace,
            session.waiting_save,
            session.history.before is not None,
        )
        selection = (self.controller.selectedId, value.token, value.state)
        return session, id(session.document), context, selection

    def synchronize_review(self):
        if not self.active:
            return
        session = self.controller.session
        value = getattr(session, self.slot)
        signature = (session, value.token, value.state, session.document.revision)
        if signature == self.signature:
            return
        self.signature = signature
        state = replacement_assessments.status(session, self.slot)
        if state != self._state:
            self._state = state
            self.changed.emit()
        self.respond(state)

    def respond(self, state):
        if state["state"] == "ready":
            if not state["changes"]:
                self.apply([])
            elif self.shown != state["token"]:
                self.shown = state["token"]
                self.reviewRequested.emit()
        elif state["state"] in ("failed", "cancelled", "obsolete"):
            self.active = False
            self.controller.message = state["error"] or "Replacement assessment canceled."
            self.controller.notify()

    @Slot("QVariantList")
    def apply(self, approved):
        self.active = False
        args = dict(token=self._state.get("token", ""), approved=list(approved))
        result = self.controller.run(self.prefix + ".apply", args)
        if result:
            self.finished.emit()
        else:
            self.active = True

    @Slot()
    def cancel(self):
        self.active = False
        self.controller.run(self.prefix + ".cancel", {})
        self.finished.emit()
