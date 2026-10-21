"""Staged field colors retain displayed mesh identity and matching pick geometry."""

from anthroforge.application import tissue_inspection as inspection
from anthroforge.native import scene as native

from . import tissue_inspection_scene as scene


def rows(tool, values, resources):
    brush = tool.controller.tissue_painting
    if not brush.name or brush.target != tool.target:
        return values, resources
    value = brush.preview
    if not value or not inspection.current(tool.controller.session, value):
        return values, resources
    if not values or value["options"]["stage"] != tool.stage:
        return values, resources
    heat = value["resource"]
    return scene.heat_chunks(values[0], heat), [heat]


def obstacles(controller, target):
    seen, result = set(), []
    for row in controller.render_model.active_rows():
        if row["id"] in seen or row["id"] == target or not row["surface_visible"]:
            continue
        seen.add(row["id"])
        frame = native.geometry_matrix(
            controller.session.engine, row["matrix"], row["geometry_offset"]
        )
        result.append(dict(asset=row["geometry_asset"], frame=frame.tolist()))
    return result


def capture(tool, view):
    controller, target = tool.controller, tool.target
    row = scene.primary(controller.tissue_inspection)
    if not row or row["owner"] != target:
        raise ValueError("Waiting for the tissue stage to be displayed.")
    return dict(
        name=tool.name,
        stage=row["stage"],
        expected_asset=row["geometry_asset"],
        view=list(view),
        obstacles=obstacles(controller, target),
    )
