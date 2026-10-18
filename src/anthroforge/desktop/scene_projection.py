"""Incremental scene metadata, separate from authored definitions and render leases."""

from anthroforge.application.dependencies import closure
from anthroforge.core.entities import descendants
from anthroforge.core.results import Port, geometry_asset

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


def control_targets(document, changes, full):
    if full or control_relationships_changed(changes):
        return set(document.index.controls)
    owners = {
        key
        for key, fields in changes.entities.items()
        if fields & {"matrix", "geometry_offset", "result", "asset", "attachment"}
    }
    seeds = {Port(key, output) for key in owners for output in ("pose", "geometry")}
    seeds.update(Port(key, output) for key in changes.controls for output in ("control", "cage"))
    affected = closure(document.index.structure.dependencies.consumers, seeds)
    return set(changes.controls) | {p.owner for p in affected if p.owner in document.index.controls}


def control_relationships_changed(changes):
    fields = (*changes.entities.values(), *changes.controls.values())
    return "attachments_enabled" in changes.document or any(
        value & {"deformers", "follow", "support", "attachment"} for value in fields
    )


class SceneProjection:
    def __init__(self, controller):
        self.controller = controller
        self.session, self.cursor, self.workspace = None, -1, None
        self.records, self.keys, self.order = {}, {}, []
        self.view, self.selected = PropertyProjection(controller), PropertyProjection(controller)
        self.view.synchronize(dict(rows=[], parents=[]))
        self.selection = ()
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
        self.controller.construction.synchronize()
        self.synchronize_selection()

    def update_records(self, changes, full, structural):
        session, document = self.controller.session, self.controller.session.document
        entities = document.index.entities
        if structural:
            self.order = [*document.index.structure.order, *(c.id for c in document.controls)]
            self.records = {key: row for key, row in self.records.items() if key in self.order}
            self.keys = {key: value for key, value in self.keys.items() if key in self.order}
        targets = set(entities) if full or structural else set(changes.entities)
        for key in changes.entities:
            targets.update(document.index.structure.children.get(key, ()))
        self.update_entities(entities, targets, session.workspace)
        self.update_controls(document, changes, full or structural)

    def update_controls(self, document, changes, full):
        for key in control_targets(document, changes, full):
            if key in document.index.controls:
                self.records[key] = scene_state.control_record(
                    self.controller, document.control(key)
                )

    def update_entities(self, entities, targets, workspace):
        depths = self.controller.session.document.index.structure.depths
        for key in targets:
            if key not in entities:
                continue
            entity = entities[key]
            depth = depths[key]
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
        records = self.records | controller.construction.records
        controller.object_selection.retain(records)
        self.selected.synchronize(records.get(controller.selection, {}))
        if self.selection != tuple(controller.object_selection.items):
            self.selection = tuple(controller.object_selection.items)
            controller.selectionChanged.emit()


def initialize(controller):
    from .construction_projection import ConstructionProjection

    controller.construction = ConstructionProjection(controller)
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
        controller.render_model.publish(
            scene_state.render_rows(rows), (a.mesh for a in controller.session.assets.values())
        )
    controller.construction.publish()
    scene_state.control_picking_inputs(controller)


def render_record(row):
    names = ("id", "handle", "chunks", "matrix", "geometry_offset", "trs", "quaternion")
    names += ("visible", "pickable", "readonly", "opacity", "color", "asset", "anchors")
    names += ("surface_visible", "surface_pickable")
    return dict(
        {name: row[name] for name in names},
        geometry_asset=row.get("geometry_asset", ""),
        geometry_revision=row.get("geometry_revision", 0),
    )
