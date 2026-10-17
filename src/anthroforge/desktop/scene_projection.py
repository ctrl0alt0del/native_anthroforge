"""Incremental scene metadata, separate from authored definitions and render leases."""

from anthroforge.core.entities import descendants
from anthroforge.core.results import geometry_asset
from anthroforge.native.attachments import ordered

from . import scene_state
from .property_projection import PropertyProjection


def entity_key(entity, parent, workspace):
    fields = ("name", "parent", "matrix", "geometry_offset", "attachment", "color", "update_mode")
    fields += ("status", "error")
    support = (parent.matrix, parent.geometry_offset, geometry_asset(parent)) if parent else None
    return (
        *(getattr(entity, key) for key in fields),
        geometry_asset(entity),
        entity.primitive.kind if entity.primitive else None,
        support,
        workspace,
    )


def structural_changes(changes):
    return (
        changes.reset
        or bool(changes.document & {"entities.order", "controls.order"})
        or any(values & {"@membership", "parent"} for values in changes.entities.values())
        or any("@membership" in values for values in changes.controls.values())
    )


class SceneProjection:
    def __init__(self, controller):
        self.controller = controller
        self.session, self.cursor, self.workspace = None, -1, None
        self.records, self.keys, self.order = {}, {}, []
        self.view, self.selected = PropertyProjection(controller), PropertyProjection(controller)
        self.view.synchronize(dict(rows=[], parents=[]))
        self.selection = ""
        self._parent_key, self._parents = None, []

    def synchronize(self):
        session = self.controller.session
        changes = session.changes.since(self.cursor if session is self.session else -1)
        full = changes.reset or self.workspace != session.workspace
        self.update_records(changes, full, structural_changes(changes))
        self.session, self.cursor, self.workspace = (
            session,
            session.changes.serial,
            session.workspace,
        )
        rows = [self.records[key] for key in self.order]
        self.view.synchronize(dict(rows=rows, parents=self.parents()))
        self.controller.rows = rows
        self.synchronize_selection()

    def update_records(self, changes, full, structural):
        session, document = self.controller.session, self.controller.session.document
        entities = {e.id: e for e in document.entities}
        if structural:
            self.order = [e.id for e in ordered(document.entities)] + [
                c.id for c in document.controls
            ]
            self.records = {key: row for key, row in self.records.items() if key in self.order}
            self.keys = {key: value for key, value in self.keys.items() if key in self.order}
        targets = set(entities) if full or structural else set(changes.entities)
        targets.update(e.id for e in document.entities if e.parent in changes.entities)
        self.update_entities(entities, targets, session.workspace)
        if full or changes.entities or changes.controls:
            for control in document.controls:
                self.records[control.id] = scene_state.control_record(self.controller, control)

    def update_entities(self, entities, targets, workspace):
        depths = {}
        for key in self.order:
            if key not in entities:
                continue
            entity = entities[key]
            depth = depths[key] = depths.get(entity.parent, -1) + 1
            if key in targets:
                cache = (entity_key(entity, entities.get(entity.parent), workspace), depth)
                if self.keys.get(key) != cache:
                    self.records[key] = scene_state.record(self.controller, entity, depth)
                    self.keys[key] = cache

    def parents(self):
        document = self.controller.session.document
        selected = self.controller.selection
        key = (selected, tuple((e.id, e.parent, e.name) for e in document.entities))
        if key != self._parent_key:
            excluded = descendants(document.entities, selected) if selected else set()
            self._parents = [
                dict(id=e.id, name=e.name) for e in document.entities if e.id not in excluded
            ]
            self._parent_key = key
        return self._parents

    def synchronize_selection(self):
        controller = self.controller
        if controller.selection not in self.records:
            controller.selection = ""
        self.selected.synchronize(self.records.get(controller.selection, {}))
        if self.selection != controller.selection:
            self.selection = controller.selection
            controller.selectionChanged.emit()


def initialize(controller):
    controller.scene_projection = SceneProjection(controller)
    controller._state = PropertyProjection(controller)
    controller._render_rows = []
    scene_state.picking_inputs(controller, [])


def refresh(controller):
    projection = controller.scene_projection
    previous = projection.view.value("rows")
    projection.synchronize()
    if previous != projection.view.value("rows"):
        controller.treeChanged.emit()
    publish(controller)
    controller.authoring.refresh()


def publish(controller):
    rows = [render_record(row) for row in controller.rows]
    if rows != controller._render_rows:
        controller._render_rows = rows
        controller.render_model.publish(scene_state.render_rows(rows), controller.session.assets)
    scene_state.control_picking_inputs(controller)


def render_record(row):
    names = ("id", "handle", "chunks", "matrix", "geometry_offset", "trs", "quaternion")
    names += ("visible", "pickable", "readonly", "opacity", "color", "asset", "anchors")
    return {name: row[name] for name in names}
