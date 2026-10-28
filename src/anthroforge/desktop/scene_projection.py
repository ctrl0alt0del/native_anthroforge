"""Incremental scene metadata, separate from authored definitions and render leases."""

from anthroforge.application.dependencies import closure
from anthroforge.application.object_frames import Frames
from anthroforge.application.transform_policy import object_reason
from anthroforge.core.entities import descendants
from anthroforge.core.results import Port, geometry_asset

from . import mirror_scene, scene_state, surface_scene, tissue_projection
from .construction_changes import ConstructionChanges, relationships_changed
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
    seeds.update(Port(key, "pose") for key in changes.objects)
    affected = closure(document.index.structure.dependencies.consumers, seeds)
    return set(changes.controls) | {p.owner for p in affected if p.owner in document.index.controls}


def control_relationships_changed(changes):
    fields = (*changes.entities.values(), *changes.controls.values(), *changes.objects.values())
    return "attachments_enabled" in changes.document or any(
        value & {"deformers", "follow", "parent", "attachment"} for value in fields
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
        self.construction_changes = ConstructionChanges()

    def synchronize(self):
        session = self.controller.session
        changes = session.changes.since(self.cursor if session is self.session else -1)
        full = changes.reset or self.workspace != session.workspace
        self.update_records(changes, full, structural_changes(changes))
        self.prune_records()
        self.synchronize_objects(changes, full)
        self.remember(session)
        self.publish_records()
        mirror_scene.synchronize(self)
        self.synchronize_selection()

    def synchronize_objects(self, changes, full):
        session = self.controller.session
        targets = self.construction_changes.targets(session.document, changes, full)
        if relationships_changed(changes):
            self.controller.construction.keys.clear()
            for key in session.document.registry.authored:
                self.keys.pop(key, None)
        frames = Frames(session.engine, session.document)
        tissue_projection.synchronize(self, targets, frames)
        self.controller.construction.synchronize(targets, frames)

    def remember(self, session):
        self.session = session
        self.cursor = session.changes.serial
        self.workspace = session.workspace

    def publish_records(self):
        rows = [self.records[key] for key in self.order]
        self.view.synchronize(
            dict(rows=[r for r in rows if not r["is_control"]], parents=self.parents())
        )
        self.controller.rows = rows

    def prune_records(self):
        document = self.controller.session.document
        live = set(document.registry.anatomy) | document.index.controls.keys()
        self.order = [key for key in self.order if key in live]
        self.records = {key: row for key, row in self.records.items() if key in live}
        self.keys = {key: value for key, value in self.keys.items() if key in live}

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
        key = parent_signature(document, selected)
        if key != self._parent_key:
            excluded = descendants(document.entities, selected) if selected else set()
            self._parents = [
                dict(id=e.id, name=e.name) for e in document.entities if e.id not in excluded
            ]
            self._parents.extend(mirror_parents(document, excluded))
            self._parent_key = key
        return self._parents

    def synchronize_selection(self):
        controller = self.controller
        records = self.records | controller.construction.records | controller.mirror_records
        controller.object_selection.retain(records)
        self.selected.synchronize(selection_record(controller, records))
        if self.selection != tuple(controller.object_selection.items):
            self.selection = tuple(controller.object_selection.items)
            controller.selectionChanged.emit()


def mirror_parents(document, excluded):
    return [
        dict(id=v.id, name=document.entity(v.source).name + " · mirrored")
        for v in document.mirrors.instances.values()
        if v.source in document.index.entities and v.source not in excluded
    ]


def parent_signature(document, selected):
    return (
        selected,
        tuple((e.id, e.parent, e.name) for e in document.entities),
        tuple(document.mirrors.instances),
    )


def selection_record(controller, records):
    row = records.get(controller.selection, {})
    if not row:
        return {}
    if row.get("mirror_source"):
        return dict(row, transformable=False, transform_reason="Mirrored instances are read-only.")
    reason = object_reason(controller.session.document.object(controller.selection))
    return dict(row, transformable=not reason, transform_reason=reason)


def initialize(controller):
    from .construction_projection import ConstructionProjection
    from .record_model import RecordModel

    controller.construction = ConstructionProjection(controller)
    controller.scene_projection = SceneProjection(controller)
    controller._state = PropertyProjection(controller)
    controller._render_rows = []
    controller.mirror_records = {}
    controller._mirror_projection_cache = {}
    controller.marker_model = RecordModel(controller, ("item",), "id")
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
    from .inspection_visibility import records
    from .mirror_scene import rows as mirror_rows

    originals = [*controller.rows, *surface_scene.records(controller)]
    rows = [render_record(row) for row in mirror_rows(controller, originals)]
    rows.extend(auxiliary_rows(controller))
    rows = records(controller, rows)
    if rows != controller._render_rows:
        controller._render_rows = rows
        controller.render_model.publish(
            scene_state.render_rows(rows), surface_scene.resources(controller)
        )
    controller.construction.publish()
    scene_state.control_picking_inputs(controller)


def auxiliary_rows(controller):
    from . import skin_scene

    return [
        *surface_scene.preview_rows(controller),
        *surface_scene.tissue_preview_rows(controller),
        *skin_scene.rows(controller),
    ]


def render_record(row):
    names = ("id", "handle", "chunks", "matrix", "geometry_offset", "trs", "quaternion")
    names += ("visible", "pickable", "readonly", "opacity", "color", "asset", "anchors")
    names += ("surface_visible", "surface_pickable")
    return dict(
        {name: row[name] for name in names},
        geometry_asset=row.get("geometry_asset", ""),
        geometry_revision=row.get("geometry_revision", 0),
        context_dimmed=row.get("context_dimmed", row["readonly"]),
    )
