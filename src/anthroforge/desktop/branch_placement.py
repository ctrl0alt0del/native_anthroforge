"""Cached authored-point projection; a provisional root never changes the document."""

from anthroforge.core.construction import Curve
from anthroforge.native.components import PickIndex, transformed


class BranchPlacement:
    def __init__(self, controller):
        self.controller, self.document = controller, None
        self.index, self.rows, self.source = None, [], {}
        self.camera, self.perspective = [], False

    def invalidate(self):
        self.document = None

    def reset(self):
        self.source = {}
        self.index, self.rows, self.document = None, [], None

    def closest(self, ray, normal):
        if self.document is not self.controller.session.document:
            self.rebuild()
        origin = self.camera if self.perspective and self.camera else ray[:3]
        index = self.index.closest(origin, ray[3:6], normal, self.perspective)
        return self.rows[index] if index >= 0 else ({}, [])

    def rebuild(self):
        controller, seen = self.controller, set()
        self.rows = []
        for row in controller.path_model.active_rows():
            if row["id"] not in seen and row["pickable"] and row["visible"]:
                self.rows.extend(control_points(controller, row))
                seen.add(row["id"])
        self.index = PickIndex(controller.session.engine, [point for _, point in self.rows])
        self.document = controller.session.document


def control_points(controller, row):
    session = controller.session
    item = session.document.registry.records.get(row["id"])
    asset = session.resources.paths.get(row["geometry_asset"])
    if not isinstance(item, Curve) or asset is None:
        return []
    live = {p.id for p in item.points}
    points = [p for p in asset.authored.points if p.id in live]
    positions = transformed(session.engine, [p.position for p in points], row["matrix"])
    return [
        (dict(curve=item.id, point=p.id), v.tolist())
        for p, v in zip(points, positions, strict=True)
    ]


def update(tool, ray, normal, press):
    reference, tool.hover = tool.branch.closest(ray, normal)
    if press and not reference:
        raise ValueError("Show a pickable curve in this workspace to place a branch root.")
    if not press or not reference:
        return
    from . import drawing_context

    tool.stroke = drawing_context.capture(tool, normal)
    tool.stroke.seed(ray, tool.hover, retain_plane=tool.options["depth"] == "IMAGE")
    tool.branch.source = reference
    tool.pointsAdded.emit(tool.stroke.read().tolist())
