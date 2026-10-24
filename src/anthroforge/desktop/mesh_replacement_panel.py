"""Desktop source selection and review consume the same headless replacement operations."""

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from anthroforge.application import mesh_replacement


class MeshReplacementPanel(QObject):
    changed = Signal()
    fileRequested = Signal()
    reviewRequested = Signal()
    finished = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.target, self.path, self.shown = "", "", ""
        self.active, self.signature = False, None
        self._state = {}

    @Property("QVariantMap", notify=changed)
    def state(self):
        return self._state

    @Slot(str)
    def choose(self, target):
        if self.active:
            self.cancel()
        self.target = target
        self.fileRequested.emit()

    @Slot(str)
    def assess(self, url):
        self.path = QUrl(url).toLocalFile() if QUrl(url).isLocalFile() else url
        result = self.controller.run(
            "scp.mesh.replace.assess", dict(target=self.target, path=self.path)
        )
        self.active, self.signature = bool(result), None
        self.synchronize()

    @Slot()
    def retry(self):
        self.assess(self.path)

    def synchronize(self):
        if not self.active:
            return
        session = self.controller.session
        value = session.mesh_replacement
        signature = (session, value.token, value.state, session.document.revision)
        if signature == self.signature:
            return
        self.signature = signature
        state = mesh_replacement.status(session)
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
        result = self.controller.run(
            "scp.mesh.replace.apply",
            dict(token=self._state.get("token", ""), approved=list(approved)),
        )
        if result:
            self.finished.emit()
        else:
            self.active = True

    @Slot()
    def cancel(self):
        self.active = False
        self.controller.run("scp.mesh.replace.cancel", {})
        self.finished.emit()
