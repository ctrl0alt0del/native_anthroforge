"""Pointer workflow over displayed geometry; annotations use shared application commands."""

from dataclasses import asdict

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import bookmarks, measurements
from anthroforge.native import scene

from . import scene_state
from .values import qml


class InspectionTools(QObject):
    changed = Signal()
    bookmarkRequested = Signal(list, bool, str)

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.active = controller, False
        self.start, self.hover, self.rows, self.bookmarks = {}, {}, [], []
        self.context, self.signature = None, None

    @Property("QVariantMap", notify=changed)
    def state(self):
        return qml(
            dict(
                active=self.active,
                start=self.start,
                hover=self.hover,
                measurements=self.rows,
                bookmarks=self.bookmarks,
            )
        )

    def synchronize(self):
        session = self.controller.session
        context = (session.document.id, session.active_workspace)
        if context != self.context:
            self.active, self.start, self.hover = False, {}, {}
            self.context = context
        signature = (context, session.document.revision)
        if signature != self.signature:
            self.signature = signature
            self.rows, self.bookmarks = measurements.inspect(session), bookmarks.inspect(session)
            self.changed.emit()

    @Slot()
    def toggle(self):
        session = self.controller.session
        if session.history.before is not None or session.waiting_save:
            return
        self.controller.cancelViewportTools(self)
        self.active = not self.active
        self.start, self.hover = {}, {}
        self.changed.emit()

    @Slot()
    def cancel(self):
        self.active, self.start, self.hover = False, {}, {}
        self.changed.emit()

    @Slot("QVariantList", "QVariantList", int, bool)
    def probe(self, origin, direction, depth, confirm):
        if not self.active or self.controller.session.waiting_save:
            return
        hits = scene_state.mesh_hits(self.controller, origin, direction)
        self.hover = self.witness(hits[depth % len(hits)]) if hits else {}
        if confirm and self.hover:
            self.place()
        self.changed.emit()

    def witness(self, hit):
        row = self.controller.pick_rows[hit["id"]]
        mesh = scene_state.displayed_mesh(self.controller, row)
        engine = self.controller.session.engine
        frame = scene.geometry_matrix(engine, row["matrix"], row["geometry_offset"])
        source = dict(
            entity=row["id"],
            asset=row["geometry_asset"],
            frame=tuple(frame),
            revision=row["geometry_revision"],
            stage=row.get("stage", ""),
        )
        value = measurements.witness(engine, mesh, source, hit["triangle"], hit["weights"])
        return asdict(value)

    def place(self):
        if not self.start:
            self.start = self.hover
            return
        result = self.controller.run("measurement.add", dict(start=self.start, end=self.hover))
        if result:
            self.start = {}

    @Slot(str)
    def restoreBookmark(self, identity):
        result = self.controller.run("bookmark.restore", dict(bookmark=identity))
        if result:
            self.bookmarkRequested.emit(result["camera"], result["orthographic"], result["name"])
