"""Incremental Construction records, separate from the anatomical outliner."""

from anthroforge.application import curve_sources, workspace_policy
from anthroforge.core import presentation
from anthroforge.core.object_registry import kind
from anthroforge.native import scene

from . import surface_scene
from .construction_filter import ConstructionFilter
from .construction_metadata import describe
from .record_model import RecordModel
from .values import qml

CATEGORIES = {
    "IMAGE": "images",
    "SURFACE": "geometry",
    "MEMBRANE": "geometry",
    "TISSUE": "geometry",
}


class ConstructionProjection:
    def __init__(self, controller):
        self.controller, self.records, self.keys = controller, {}, {}
        self.rendered = {}
        self.model = RecordModel(controller, ("item",), "id")
        self.browser = ConstructionFilter(self.model)
        from .path_placeholders import PathPlaceholders
        from .point_scene import PointScene

        self.points = PointScene(controller)
        self.placeholders = PathPlaceholders()

    def synchronize(self):
        session = self.controller.session
        live = set(session.document.registry.construction) | session.document.index.controls.keys()
        self.records = {key: row for key, row in self.records.items() if key in live}
        self.keys = {key: value for key, value in self.keys.items() if key in live}
        for item in session.document.registry.construction.values():
            self.update_record(session, item)
        for item in session.document.controls:
            self.records[item.id] = self.controller.scene_projection.records[item.id]
        self.model.synchronize_records(
            [dict(id=key, item=row) for key, row in self.records.items()]
        )
        self.points.synchronize(self.records)

    def update_record(self, session, item):
        frame = curve_sources.world(session.engine, session.document, item.id)
        owners = workspace_policy.associations(session.document, item.id)
        key = (item, frame, session.workspace, owners)
        if key != self.keys.get(item.id):
            self.records[item.id], self.keys[item.id] = record(session, item, frame), key

    def publish(self):
        from . import image_scene, path_scene

        resources = self.controller.session.resources
        self.publish_fibers(resources)
        self.publish_kind(
            "path",
            path_scene.rows(self.controller)
            + path_scene.preview_rows(self.controller)
            + self.placeholders.rows(self.controller),
            (*path_scene.resources(self.controller), *self.placeholders.resources()),
        )
        self.publish_kind("image", image_scene.rows(self.controller), resources.images.values())

    def publish_fibers(self, resources):
        mirrored = {
            r["mirror_source"] for r in self.controller.mirror_records.values() if r["visible"]
        }
        rows = [
            r
            for r in self.records.values()
            if r.get("asset") in resources.paths and (r["visible"] or r["id"] in mirrored)
        ]
        self.controller.fiber_display.synchronize(rows)

    def publish_kind(self, kind, desired, resources):
        if desired != self.rendered.get(kind):
            self.rendered[kind] = desired
            getattr(self.controller, kind + "_model").publish(desired, resources)


def record(session, item, frame):
    names = ("id", "name", "parent", "update_mode")
    row = {name: getattr(item, name) for name in names}
    row.update(kind=kind(item), **result_record(item.result))
    row.update(is_construction=True, is_control=False, color="#65c9d6", geometry_offset=[0, 0, 0])
    row.update(matrix=frame, trs=session.engine.decompose(frame), asset=item.result.asset)
    row.update(
        local_trs=session.engine.decompose(item.matrix),
        quaternion=scene.quaternion(session.engine, frame),
    )
    row.update(**flags(session, item), **describe(session, item))
    return qml(dict(row, **surface_scene.metadata(session, item, row)))


def result_record(result):
    return dict(status=result.status, error=result.error, geometry_revision=result.revision)


def flags(session, item):
    readonly = not workspace_policy.included(session.document, session.workspace, item.id)
    category = CATEGORIES.get(kind(item), "curves")
    visible = item.id not in session.workspace.hidden and presentation.visible(
        session.workspace, category
    )
    return dict(
        readonly=readonly,
        visible=visible,
        pickable=visible
        and not readonly
        and item.id not in session.workspace.unpickable
        and presentation.pickable(session.workspace, category),
        unassigned=not workspace_policy.associations(session.document, item.id),
    )
