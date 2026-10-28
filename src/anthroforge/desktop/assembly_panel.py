"""Desktop projection of the shared import session; preparation never adopts the source."""

from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot

from . import assembly_projection
from .choice_model import ChoiceModel


class AssemblyPanel(QObject):
    changed = Signal()
    requested = Signal()
    finished = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.anatomy, self.construction = ChoiceModel(self), ChoiceModel(self)
        self.anatomy.edited.connect(lambda rows: self.selection_changed(rows, True))
        self.construction.edited.connect(lambda rows: self.selection_changed(rows, False))
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(180)
        self.timer.timeout.connect(self.prepare)
        self.reset()

    def reset(self):
        self.active, self.repair = False, False
        self.selected, self.mappings, self.options = set(), {}, {}
        self._state, self._references, self._targets, self._properties = {}, [], [], []
        self.focus, self.target, self.signature = "", {}, None
        self.anatomy.synchronize([])
        self.construction.synchronize([])

    @Property(QObject, constant=True)
    def anatomyModel(self):
        return self.anatomy

    @Property(QObject, constant=True)
    def constructionModel(self):
        return self.construction

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            self._state,
            repair=self.repair,
            reference=self.focus,
            target=self.target,
            parent=self.options.get("parent", ""),
            options=self.options,
            parents=assembly_projection.parents(self),
        )

    @Property("QVariantList", notify=changed)
    def references(self):
        return self._references

    @Property("QVariantList", notify=changed)
    def targets(self):
        return self._targets

    @Property("QVariantList", notify=changed)
    def properties(self):
        return self._properties

    @Slot(str)
    def inspect(self, url):
        self.cancel()
        self.reset()
        self.active = True
        path = QUrl(url).toLocalFile() if QUrl(url).isLocalFile() else url
        selected = self.controller.selectedId
        document = self.controller.session.document
        self.options["parent"] = selected if selected in document.index.entities else ""
        self.controller.run("assembly.inspect", dict(path=path))
        self.synchronize()
        self.requested.emit()

    @Slot(str)
    def resolve(self, reference):
        self.cancel()
        self.reset()
        self.active = self.repair = True
        self._references = assembly_projection.pending(self)
        self._state = dict(state="idle", ready=False)
        self.selectReference(reference or (self._references[0]["key"] if self._references else ""))
        self.requested.emit()

    def selection_changed(self, rows, anatomy):
        model = self.anatomy if anatomy else self.construction
        editable = {r["key"] for r in model.records.rows if not r["locked"]}
        self.selected = (self.selected - editable) | (set(rows) & editable)
        self.queue()

    @Slot(str, "QVariant")
    def option(self, name, value):
        self.options[name] = value
        self.queue()

    def queue(self):
        self._state = dict(self._state, ready=False, state="preparing", error="")
        self.changed.emit()
        self.timer.start()

    @Slot()
    def prepare(self):
        session = self.controller.session
        if self.repair:
            self.controller.run("assembly.resolve", dict(mappings=self.mappings))
        elif self.selected and session.assembly.source.state == "ready":
            self.controller.run("assembly.prepare", self.arguments())
        else:
            session.assembly.cancel_preparation()
        self.signature = None
        self.synchronize()

    def arguments(self):
        return dict(
            source=self.controller.session.assembly.source.token,
            selected=sorted(self.selected),
            mappings=self.mappings,
            **self.options,
        )

    def synchronize(self):
        if not self.active or self.timer.isActive():
            return
        manager = self.controller.session.assembly
        if self.stale(manager):
            self.queue()
            return
        signature = assembly_projection.signature(manager)
        if signature == self.signature:
            return
        self.signature = signature
        self._state = manager.status()
        assembly_projection.synchronize(self)
        self.changed.emit()

    def stale(self, manager):
        from anthroforge.core.jobs import ObsoleteInputs

        candidate = manager.preparation.candidate
        if candidate is None:
            return False
        try:
            candidate.reads.require(self.controller.session.document)
        except ObsoleteInputs:
            return True
        return False

    @Slot(str)
    def selectReference(self, key):
        self.focus = key
        self.target, self._properties = {}, []
        self._targets = assembly_projection.targets(self)
        self.changed.emit()

    @Slot("QVariantMap")
    def selectTarget(self, target):
        self.target = dict(target)
        self._properties = assembly_projection.properties(self, target["target"])
        if not self.current().get("property"):
            self.mapTarget({})
        self.changed.emit()

    def current(self):
        return next((r for r in self._references if r["key"] == self.focus), {})

    @Slot("QVariantMap")
    def mapTarget(self, prop):
        value = dict(action="map", target=self.target["target"], instance=self.target["instance"])
        if prop:
            value["property"] = dict(prop)
        self.mappings[self.focus] = value
        self.queue()

    @Slot(str)
    def action(self, action):
        value = dict(self.mappings.get(self.focus, {}))
        if action == "rebind":
            value["rebind"] = not value.get("rebind", False)
        else:
            value = dict(action=action)
        self.mappings[self.focus] = value
        self.queue()

    @Slot()
    def apply(self):
        result = self.controller.run("assembly.import", dict(token=self._state.get("token", "")))
        if result:
            self.active = False
            self.finished.emit()

    @Slot()
    def cancel(self):
        self.timer.stop()
        if self.active:
            self.controller.session.assembly.cancel()
        self.active = False
