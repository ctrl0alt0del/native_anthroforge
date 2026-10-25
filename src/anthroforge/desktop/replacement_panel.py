"""Shared desktop review lifecycle; producers own source selection and application policies."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import replacement_assessments


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

    @Property("QVariantMap", notify=changed)
    def state(self):
        return self._state

    @Property(str, constant=True)
    def heading(self):
        return self._heading

    @Slot(str)
    def choose(self, target):
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
