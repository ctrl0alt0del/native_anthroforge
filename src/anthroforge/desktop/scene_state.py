"""Presentation projection and cached batch picking inputs."""

from dataclasses import asdict
from time import perf_counter as monotonic

import numpy as np

from anthroforge.native import scene
from anthroforge.native.attachments import anchor_points, ordered


def record(controller, entity, depth):
    session = controller.session
    row = asdict(entity)
    row["geometry_offset"] = list(entity.geometry_offset)
    row.update(depth=depth, trs=session.engine.decompose(entity.matrix))
    row["quaternion"] = scene.quaternion(session.engine, entity.matrix)
    row.update(presentation_flags(session.workspace, entity.id))
    row["anchors"] = markers(session, entity)
    row["opacity"] = 0.08 if row["readonly"] else 1.0
    row["handle"] = session.assets[entity.asset].mesh.handle if entity.asset else 0
    row["chunks"] = session.assets[entity.asset].mesh.counts[4] if entity.asset else 0
    return row


def presentation_flags(workspace, entity):
    readonly = workspace.focused and entity not in workspace.members
    visible = entity not in workspace.hidden
    return dict(
        readonly=readonly,
        visible=visible,
        pickable=visible and entity not in workspace.unpickable and not readonly,
    )


def markers(session, entity):
    if not entity.parent or not entity.attachment.binding:
        return []
    parent = session.document.entity(entity.parent)
    handle = session.assets[parent.asset].mesh.handle if parent.asset else 0
    try:
        return anchor_points(session.engine, entity, parent, handle)
    except ValueError:
        return []


def records(controller):
    rows, depths = [], {}
    for entity in ordered(controller.session.document.entities):
        depth = depths.get(entity.parent, -1) + 1
        depths[entity.id] = depth
        rows.append(record(controller, entity, depth))
    return rows


def render_rows(rows):
    return [
        dict(row, key=f"{row['id']}:{row['handle']}:{chunk}", chunk=chunk)
        for row in rows
        if row["visible"]
        for chunk in range(row["chunks"])
    ]


def picking_inputs(controller, rows):
    eligible = [row for row in rows if row["pickable"] and row["handle"]]
    controller.pick_ids = [row["id"] for row in eligible]
    controller.pick_handles = np.array([row["handle"] for row in eligible], dtype=np.uint64)
    matrices = [
        scene.geometry_matrix(controller.session.engine, row["matrix"], row["geometry_offset"])
        for row in eligible
    ]
    controller.pick_matrices = np.ascontiguousarray(matrices, dtype=np.float64)


def picked(controller, origin, direction, depth):
    started = monotonic()
    try:
        return pick_scene(controller, origin, direction, depth)
    finally:
        controller.session.scheduler.metrics.observe("picking", monotonic() - started)


def pick_scene(controller, origin, direction, depth):
    if not controller.pick_ids:
        return {}
    hits = scene.pick(
        controller.session.engine,
        controller.pick_handles,
        controller.pick_matrices,
        origin,
        direction,
    )
    if not hits:
        return {}
    hit = hits[depth % len(hits)]
    return hit_record(controller.pick_ids, hit)


def hit_record(ids, hit):
    return {
        "id": ids[int(hit[0])],
        "distance": hit[1],
        "face": int(hit[2]),
        "triangle": int(hit[3]),
        "vertex": int(hit[4]),
        "point": hit[5:8],
    }
