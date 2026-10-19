"""Provisional support-region selection over the displayed native tissue revision."""

from dataclasses import asdict

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import tissue_fields, tissue_stack_operations
from anthroforge.application.tissue_operations import tissue
from anthroforge.core.tissue_stacking import StackRelationship
from anthroforge.native import scene, tissue_regions


class TissueRegionTools(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.options, self.selected, self.hover, self.outline = {}, set(), None, []
        self.cover, self.side, self.context, self.error = "", "a", None, ""
        self.display_key = None

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            active=bool(self.options),
            count=len(self.selected),
            error=self.error,
            target=self.options.get("target", ""),
            cover=self.cover,
            lines=self.outline,
        )

    @Slot("QVariantMap")
    def begin(self, options):
        self.attempt(self.start, dict(options))

    def start(self, options):
        session = self.controller.session
        if session.history.before is not None or session.waiting_save:
            raise ValueError("Finish the current edit before selecting support regions.")
        item = tissue(session, self.controller.selection)
        other = session.document.object(options["other"])
        row = StackRelationship(**options)
        tissue_stack_operations.require_available(item, other, row)
        if row.mode == "AUTO":
            raise ValueError("Choose Requested or Explicit order before selecting its footprint.")
        self.initialize(item, other, row)
        self.focus()
        self.redraw()

    def focus(self):
        self.controller.authoring.setEditing(False)
        self.controller.cancelViewportTools(self)

    def initialize(self, item, other, row):
        previous = previous_relationship(item, row)
        self.options = dict(asdict(row), target=item.id)
        self.cover = item.id if row.cover == "SELF" else other.id
        self.side = row.side if row.cover == "SELF" else row.other_side
        self.selected = set(previous.regions if previous and previous.cover == row.cover else ())
        self.hover, self.error = None, ""
        cover = self.controller.session.document.object(self.cover)
        self.options["topology"] = tissue_fields.domain(
            self.controller.session.resources, cover, "BASE"
        )[1]
        self.context = self.signature()

    def signature(self):
        session = self.controller.session
        keys = (self.options["target"], self.options["other"])
        items = [session.document.registry.records.get(k) for k in keys]
        return (
            session.document.id,
            session.active_workspace,
            self.controller.selection,
            tuple(
                (o.generation, o.base_result.asset, o.rest_result.asset) if o else None
                for o in items
            ),
        )

    def synchronize(self):
        if not self.options:
            return
        if self.controller.selection != self.options["target"]:
            self.cancel()
        elif self.context != self.signature():
            if not self.error:
                self.error = "Tissue inputs changed. Cancel and select the support region again."
                self.outline = []
                self.changed.emit()
        elif self.current_display_key() != self.display_key:
            self.redraw()

    def current_display_key(self):
        row = self.controller.pick_rows.get(self.cover, {})
        return row.get("handle"), tuple(row.get("matrix", ()))

    def displayed(self):
        row = self.controller.pick_rows.get(self.cover)
        if not row or not row.get("surface_pickable"):
            return None
        mesh = self.controller.render_model.leases.get(row["handle"])
        frame = scene.geometry_matrix(
            self.controller.session.engine, row["matrix"], row["geometry_offset"]
        )
        return (mesh, frame) if mesh else None

    @Slot("QVariantList", "QVariantList", bool)
    def probe(self, origin, direction, confirm):
        self.attempt(self.pick, origin, direction, confirm)

    def pick(self, origin, direction, confirm):
        self.synchronize()
        displayed = self.displayed()
        if not self.options or self.error or displayed is None:
            return
        mesh, frame = displayed
        hit = mesh.engine.pick(mesh, frame, origin, direction)
        face = tissue_regions.face(mesh, int(hit[1]), self.side) if hit else None
        parts = self.controller.session.document.object(self.cover).base_state.parts
        hovered = (parts[face[0]], face[1]) if face else None
        if confirm and hovered:
            self.selected.symmetric_difference_update((hovered,))
        if confirm or self.hover != hovered:
            self.hover = hovered
            self.redraw()

    def redraw(self):
        displayed = self.displayed()
        self.display_key, self.outline = self.current_display_key(), []
        if displayed and not self.error:
            mesh, frame = displayed
            parts = self.controller.session.document.object(self.cover).base_state.parts
            chosen = self.selected | ({self.hover} if self.hover else set())
            pairs = [(parts.index(p), f) for p, f in chosen if p in parts]
            self.outline = tissue_regions.lines(mesh, pairs, self.side, frame).tolist()
        self.changed.emit()

    @Slot()
    def clear(self):
        self.selected, self.hover = set(), None
        self.redraw()

    @Slot()
    def accept(self):
        self.attempt(self.commit)

    def commit(self):
        self.synchronize()
        if self.error or not self.options:
            raise ValueError(self.error or "No support-region draft is active.")
        arguments = dict(self.options, regions=sorted(self.selected))
        self.controller.session.command("tissue.stacking.relationship", **arguments)
        self.cancel()
        self.controller.refresh()

    @Slot()
    def cancel(self):
        if not self.options:
            return
        self.options, self.selected, self.hover, self.outline = {}, set(), None, []
        self.error = ""
        self.changed.emit()

    def attempt(self, action, *args):
        try:
            action(*args)
        except (ValueError, KeyError) as error:
            self.controller.message = str(error)
            self.controller.notify()


def previous_relationship(item, row):
    return next(
        (
            r
            for r in item.stack_relationships
            if tissue_stack_operations.pair(r) == tissue_stack_operations.pair(row)
        ),
        None,
    )
