"""Candidate-only staged views; native picking reads exactly the displayed resources."""

from dataclasses import replace
from types import SimpleNamespace

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application.inspection_context import InspectionContext
from anthroforge.core.entities import SCP
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import scene

from . import comparison_picking, shortcut_comparison_scene, skeleton_display
from .models import PublicationGroup, RenderModel


class SkeletonScene(QObject):
    changed = Signal()
    selected = Signal(str)
    annotationsChanged = Signal()

    def __init__(self, controller, parent):
        super().__init__(parent)
        self.controller, self.candidate = controller, None
        self.models = (RenderModel(controller), RenderModel(controller))
        self.publication = PublicationGroup(self.models)
        self.filters = dict(bones=True, fibers=True, tissues=True, attachments=True, skin=True)
        self.camera = [0.0, 0.0, 0.0, -18.0, 25.0, 8.0]
        self.mode, self.selection, self.picking = "Split", "", [None, None]
        self.marker_rows = []
        for index, model in enumerate(self.models):
            model.activated.connect(lambda i=index: self.prepare_picking(i))

    @Property(QObject, constant=True)
    def before(self):
        return self.models[0]

    @Property(QObject, constant=True)
    def after(self):
        return self.models[1]

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            camera=self.camera,
            mode=self.mode,
            filters=self.filters,
            selection=self.selection,
        )

    @Property("QVariantList", notify=annotationsChanged)
    def anchors(self):
        return self.marker_rows

    def refresh_annotations(self):
        self.marker_rows = skeleton_display.anchors(
            self.candidate, self.selection, self.filters["attachments"]
        )
        self.annotationsChanged.emit()

    def synchronize(self, candidate):
        if candidate is self.candidate:
            return
        first = self.candidate is None
        self.candidate = candidate
        self.publish()
        if first and candidate:
            self.focus("")

    def publish(self):
        self.refresh_annotations()
        for index, model in enumerate(self.models):
            rows, leases = self.rows(index) if self.candidate else ([], [])
            model.publish(rows, leases)
        self.changed.emit()

    def rows(self, index):
        c = self.candidate
        document = c.baseline if index == 0 else c.document
        workspace = replace(document.workspaces[0], hidden=(), hidden_categories=())
        context = InspectionContext(
            document, c.resources, self.controller.session.engine, workspace
        )
        return self.context_rows(context, workspace)

    def context_rows(self, context, workspace):
        c, document = self.candidate, context.document
        rows, leases = shortcut_comparison_scene.rows(SimpleNamespace(source=context), workspace)
        affected = {p.owner for p in c.prepared} | {r.target for r in c.changes}
        rows = [r for r in rows if r["id"] in affected and self.visible(document.object(r["id"]))]
        rows += skeleton_display.mirrors(context, rows)
        if self.filters["skin"]:
            extra, owned = skeleton_display.skin(context)
            rows.extend(extra)
            leases.extend(owned)
        return rows, leases

    def visible(self, item):
        group = (
            "bones"
            if isinstance(item, SCP)
            else "tissues"
            if isinstance(item, TissueVCP)
            else "fibers"
        )
        return self.filters[group]

    @Slot(str, bool)
    def filter(self, name, enabled):
        if name in self.filters:
            self.filters[name] = enabled
            self.publish()

    @Slot(str)
    def setMode(self, mode):
        if mode in ("Split", "Before", "After", "Overlay"):
            self.mode = mode
            self.changed.emit()

    @Slot(float, float)
    def orbit(self, x, y):
        self.camera[3] = max(-89.0, min(89.0, self.camera[3] + y * 0.3))
        self.camera[4] += x * 0.3
        self.changed.emit()

    @Slot(float)
    def zoom(self, delta):
        self.camera[5] = max(0.001, min(100000.0, self.camera[5] * pow(0.9, delta / 120)))
        self.changed.emit()

    @Slot(str)
    def focus(self, key):
        self.selection = key
        self.refresh_annotations()
        rows = [
            r
            for m in self.models
            for r in m.wanted.values()
            if r["kind"] == "MESH" and (not key or r["id"] == key)
        ]
        if rows:
            self.fit(rows)
        self.changed.emit()

    def fit(self, rows):
        bounds = scene.bounds(
            self.controller.session.engine, [r["handle"] for r in rows], [r["matrix"] for r in rows]
        )
        center = [(bounds[i] + bounds[i + 3]) * 0.5 for i in range(3)]
        span = max(bounds[i + 3] - bounds[i] for i in range(3))
        self.camera = [*center, *self.camera[3:5], max(0.01, span * 1.8)]

    def prepare_picking(self, index):
        self.picking[index] = comparison_picking.capture(self.models[index])

    @Slot(int, "QVariantList", "QVariantList", float, result=str)
    def pick(self, index, origin, direction, radius):
        key = comparison_picking.pick(
            self.controller.session.engine, self.picking[index], origin, direction, radius
        )
        if key:
            self.selection = key
            self.refresh_annotations()
            self.selected.emit(key)
            self.changed.emit()
        return key
