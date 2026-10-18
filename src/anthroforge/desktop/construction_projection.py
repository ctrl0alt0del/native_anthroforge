"""Incremental Construction records, separate from the anatomical outliner."""

from anthroforge.application import curve_sources, workspace_policy
from anthroforge.core.object_registry import kind
from anthroforge.native import scene

from .record_model import RecordModel


class ConstructionProjection:
    def __init__(self, controller):
        self.controller, self.records, self.keys = controller, {}, {}
        self.model = RecordModel(controller, ("item",), "id")

    def synchronize(self):
        session = self.controller.session
        live = set(session.document.registry.construction)
        self.records = {key: row for key, row in self.records.items() if key in live}
        self.keys = {key: value for key, value in self.keys.items() if key in live}
        for item in session.document.objects:
            frame = curve_sources.world(session.engine, session.document, item.id)
            key = (item, frame, session.workspace)
            if key != self.keys.get(item.id):
                self.records[item.id], self.keys[item.id] = record(session, item, frame), key
        self.model.synchronize_records(
            [dict(id=key, item=row) for key, row in self.records.items()]
        )


def record(session, item, frame):
    names = ("id", "name", "parent", "update_mode")
    row = {name: getattr(item, name) for name in names}
    row.update(kind=kind(item), status=item.result.status, error=item.result.error)
    row.update(is_construction=True, is_control=False, color="#65c9d6", geometry_offset=[0, 0, 0])
    row.update(matrix=frame, trs=session.engine.decompose(frame), asset=item.result.asset)
    row.update(
        local_trs=session.engine.decompose(item.matrix),
        quaternion=scene.quaternion(session.engine, frame),
    )
    return dict(row, **flags(session, item))


def flags(session, item):
    readonly = not workspace_policy.included(session.document, session.workspace, item.id)
    visible = item.id not in session.workspace.hidden
    return dict(
        readonly=readonly,
        visible=visible,
        pickable=visible and not readonly and item.id not in session.workspace.unpickable,
        unassigned=not workspace_policy.associations(session.document, item.id),
    )
