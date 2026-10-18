"""Incremental Construction records, separate from the anatomical outliner."""

from anthroforge.application import curve_sources, workspace_policy
from anthroforge.core import presentation
from anthroforge.core.object_registry import kind
from anthroforge.native import scene

from .record_model import RecordModel
from .values import qml


class ConstructionProjection:
    def __init__(self, controller):
        self.controller, self.records, self.keys = controller, {}, {}
        self.rendered = []
        self.model = RecordModel(controller, ("item",), "id")

    def synchronize(self):
        session = self.controller.session
        live = set(session.document.registry.construction)
        self.records = {key: row for key, row in self.records.items() if key in live}
        self.keys = {key: value for key, value in self.keys.items() if key in live}
        for item in session.document.objects:
            self.update_record(session, item)
        self.model.synchronize_records(
            [dict(id=key, item=row) for key, row in self.records.items()]
        )

    def update_record(self, session, item):
        frame = curve_sources.world(session.engine, session.document, item.id)
        owners = workspace_policy.associations(session.document, item.id)
        key = (item, frame, session.workspace, owners)
        if key != self.keys.get(item.id):
            self.records[item.id], self.keys[item.id] = record(session, item, frame), key

    def publish(self):
        from .path_scene import rows

        desired = rows(self.controller)
        if desired != self.rendered:
            self.rendered = desired
            resources = self.controller.session.resources.paths.values()
            self.controller.path_model.publish(desired, (asset.path for asset in resources))


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
    return qml(dict(row, **flags(session, item)))


def result_record(result):
    return dict(status=result.status, error=result.error, geometry_revision=result.revision)


def flags(session, item):
    readonly = not workspace_policy.included(session.document, session.workspace, item.id)
    category = {"IMAGE": "images", "SURFACE": "geometry"}.get(kind(item), "curves")
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
