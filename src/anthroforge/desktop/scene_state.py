"""Presentation projection and cached batch picking inputs."""

from dataclasses import asdict
from time import perf_counter as monotonic

import numpy as np

from anthroforge.core.presentation import pickable, visible
from anthroforge.core.results import geometry_asset
from anthroforge.native import components, scene
from anthroforge.native.attachments import anchor_points, ordered

from .presentation import geometry_flags
from .values import qml


def record(controller, entity, depth):
    session = controller.session
    row = entity_metadata(entity)
    row["geometry_offset"] = list(entity.geometry_offset)
    row.update(depth=depth, trs=session.engine.decompose(entity.matrix))
    row["quaternion"] = scene.quaternion(session.engine, entity.matrix)
    row.update(presentation_flags(session.workspace, entity.id))
    row.update(geometry_flags(session.workspace, row))
    row["anchors"] = markers(session, entity)
    row["opacity"] = 0.08 if row["readonly"] else 1.0
    row.update(geometry_metadata(session, entity))
    return qml(row)


def entity_metadata(entity):
    names = ("id", "name", "parent", "asset", "matrix", "color", "update_mode", "status", "error")
    row = {name: getattr(entity, name) for name in names}
    row["attachment"] = asdict(entity.attachment)
    row["primitive"] = {"kind": entity.primitive.kind} if entity.primitive else None
    return row


def geometry_metadata(session, entity):
    key = geometry_asset(entity)
    mesh = session.assets[key].mesh if key else None
    return dict(
        handle=mesh.handle if mesh else 0,
        chunks=mesh.counts[4] if mesh else 0,
        is_control=False,
        geometry_asset=key,
        geometry_revision=entity.result.revision,
    )


def control_record(controller, control):
    from anthroforge.application.control_frames import display_frame
    from anthroforge.application.control_operations import affected

    session = controller.session
    matrix = display_frame(session, control)
    row = control_metadata(control, matrix)
    row.update(
        trs=session.engine.decompose(matrix), quaternion=scene.quaternion(session.engine, matrix)
    )
    row.update(control_flags(session.workspace, control))
    row.update(surface_visible=False, surface_pickable=False)
    row.update(opacity=0.08 if row["readonly"] else 1, affected=affected(session, control.id))
    return qml(row)


def control_metadata(control, matrix):
    row = dict(
        id=control.id,
        name=control.name,
        kind=control.kind,
        follow=control.follow,
        parent="",
        asset="",
        status=control.result.status,
        error=control.result.error,
    )
    row.update(depth=0, handle=0, chunks=0, anchors=[])
    row.update(geometry_offset=[0, 0, 0], matrix=matrix, is_control=True, color="#dfaf6c")
    return row


def presentation_flags(workspace, entity):
    readonly = workspace.focused and entity not in workspace.members
    visible = entity not in workspace.hidden
    return dict(
        readonly=readonly,
        visible=visible,
        pickable=visible and entity not in workspace.unpickable and not readonly,
    )


def control_flags(workspace, control):
    flags = presentation_flags(workspace, control.id)
    category = "cages" if control.kind == "LATTICE" else "hooks"
    flags["visible"] &= visible(workspace, category)
    flags["pickable"] &= pickable(workspace, category)
    return flags


def markers(session, entity):
    if not entity.parent or not entity.attachment.binding:
        return []
    parent = session.document.entity(entity.parent)
    key = geometry_asset(parent)
    handle = session.assets[key].mesh.handle if key else 0
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
    rows.extend(
        control_record(controller, control) for control in controller.session.document.controls
    )
    return rows


def render_rows(rows):
    return [
        dict(row, key=f"{row['id']}:{row['handle']}:{chunk}", chunk=chunk)
        for row in rows
        if row["surface_visible"]
        for chunk in range(row["chunks"])
    ]


def picking_inputs(controller, rows):
    snapping_inputs(controller, rows)
    eligible = [row for row in rows if row["surface_pickable"] and row["handle"]]
    controller.pick_rows = {row["id"]: row for row in eligible}
    controller.pick_ids = [row["id"] for row in eligible]
    controller.pick_handles = np.array([row["handle"] for row in eligible], dtype=np.uint64)
    matrices = [
        scene.geometry_matrix(controller.session.engine, row["matrix"], row["geometry_offset"])
        for row in eligible
    ]
    controller.pick_matrices = np.ascontiguousarray(matrices, dtype=np.float64)
    control_picking_inputs(controller)


def snapping_inputs(controller, rows):
    eligible = [row for row in rows if row["surface_visible"] and row["handle"]]
    controller.snap_ids = [row["id"] for row in eligible]
    controller.snap_handles = np.array([row["handle"] for row in eligible], dtype=np.uint64)
    controller.snap_matrices = np.ascontiguousarray(
        [
            scene.geometry_matrix(controller.session.engine, row["matrix"], row["geometry_offset"])
            for row in eligible
        ],
        dtype=np.float64,
    )


def control_picking_inputs(controller):
    eligible = [r for r in controller.rows if r["pickable"] and not r["handle"]]
    controller.pick_control_ids = [row["id"] for row in eligible]
    controller.pick_control_points = np.ascontiguousarray(
        [row["trs"][:3] for row in eligible], dtype=np.float64
    )


def picked(controller, origin, direction, depth, radius):
    started = monotonic()
    try:
        return pick_scene(controller, origin, direction, depth, radius)
    finally:
        controller.session.scheduler.metrics.observe("picking", monotonic() - started)


def mesh_hits(controller, origin, direction):
    if not controller.pick_ids:
        return []
    hits = scene.pick(
        controller.session.engine,
        controller.pick_handles,
        controller.pick_matrices,
        origin,
        direction,
    )
    return [hit_record(controller.pick_ids, hit) for hit in hits]


def control_hits(controller, origin, direction, radius):
    hits = components.hits(
        controller.session.engine, controller.pick_control_points, origin, direction, radius
    )
    return [
        dict(
            id=controller.pick_control_ids[int(index)],
            distance=distance,
            face=-1,
            triangle=-1,
            vertex=-1,
            point=controller.pick_control_points[int(index)].tolist(),
        )
        for index, distance in hits
    ]


def pick_scene(controller, origin, direction, depth, radius):
    from .path_scene import hits as path_hits

    hits = mesh_hits(controller, origin, direction) + control_hits(
        controller, origin, direction, radius
    )
    hits += path_hits(controller, origin, direction, radius)
    hits.sort(key=lambda hit: hit["distance"])
    return hits[depth % len(hits)] if hits else {}


def hit_record(ids, hit):
    return {
        "id": ids[int(hit[0])],
        "distance": hit[1],
        "face": int(hit[2]),
        "triangle": int(hit[3]),
        "vertex": int(hit[4]),
        "point": hit[5:8],
        "weights": hit[8:11],
    }
