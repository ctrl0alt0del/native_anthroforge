"""Image stages, presentation and native picking use one displayed content revision."""

import numpy as np

from anthroforge.native import images

from .inspection_visibility import records


def rows(controller):
    resources = controller.session.resources.images
    return [
        dict(
            row,
            handle=resources[row["source"]].handle,
            chunk=chunk,
            content=dict(dimensions=row["dimensions"], layer=row["image_style"]["depth"]),
            geometry_asset=row["source"],
            key=f"{row['id']}:{row['source']}:{row['image_style']['depth']}:{chunk}",
        )
        for row in records(controller, controller.construction.records.values())
        if row["kind"] == "IMAGE" and row["visible"] and row["source"] in resources
        for chunk in range(resources[row["source"]].chunks)
    ]


def prepare_picking(controller):
    displayed = controller.image_model.active_rows()
    eligible = [row for row in displayed if can_pick(row)]
    controller.image_pick_rows = eligible
    controller.image_matrices = np.ascontiguousarray([row["matrix"] for row in eligible])
    controller.image_sizes = np.ascontiguousarray(
        [row["content"]["dimensions"] for row in eligible]
    )
    controller.image_sides = np.array(
        [("BOTH", "FRONT", "BACK").index(row["image_style"]["side"]) for row in eligible],
        dtype=np.int32,
    )


def can_pick(row):
    return (
        row["pickable"]
        and row["visible"]
        and row["image_style"]["pickable"]
        and row["image_style"]["opacity"] > 0
    )


def hits(controller, origin, direction):
    records = images.pick(
        controller.session.engine,
        controller.image_matrices,
        controller.image_sizes,
        controller.image_sides,
        origin,
        direction,
    )
    visible = view_mask(controller, controller.image_pick_rows, controller.image_matrices)
    return [
        hit_record(controller.image_pick_rows[int(row[0])], row)
        for row in records
        if visible[int(row[0])]
    ]


def view_mask(controller, rows, frames):
    projection = "orthographic" if controller.viewport_view.orthographic else "perspective"
    restricted = [row["image_style"].get("only_axis_aligned", False) for row in rows]
    aligned = (
        images.aligned(controller.session.engine, frames, controller.viewport_view.direction)
        if any(restricted)
        else ()
    )
    return [
        row["image_style"][projection] and (not restricted[i] or bool(aligned[i]))
        for i, row in enumerate(rows)
    ]


def hit_record(item, hit):
    return dict(
        id=item["id"],
        distance=hit[1],
        uv=hit[2:4].tolist(),
        point=hit[4:7].tolist(),
        face=-1,
        triangle=-1,
        vertex=-1,
        layer={"FRONT": -1, "NORMAL": 0, "BACK": 1}[item["content"]["layer"]],
    )


def probe(controller, target, origin, direction):
    rows = controller.image_model.active_rows()
    row = next((r for r in rows if r["id"] == target and r["visible"]), None)
    if row is None or not view_mask(controller, [row], [row["matrix"]])[0]:
        return {}
    side = ("BOTH", "FRONT", "BACK").index(row["image_style"]["side"])
    hits = images.pick(
        controller.session.engine,
        [row["matrix"]],
        [row["content"]["dimensions"]],
        [side],
        origin,
        direction,
    )
    return hit_record(row, hits[0]) if len(hits) else {}
