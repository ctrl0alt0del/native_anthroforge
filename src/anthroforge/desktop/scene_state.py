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
    row.update(control_flags(session, control))
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


def control_flags(session, control):
    from anthroforge.application.workspace_policy import associations, included

    workspace = session.workspace
    readonly = not included(session.document, workspace, control.id)
    flags = dict(
        readonly=readonly,
        visible=control.id not in workspace.hidden,
        pickable=not readonly and control.id not in workspace.unpickable,
        unassigned=not associations(session.document, control.id),
    )
    category = "cages" if control.kind == "LATTICE" else "hooks"
    flags["visible"] &= visible(workspace, category)
    flags["pickable"] &= flags["visible"] and pickable(workspace, category)
    return flags


def markers(session, entity):
    if not entity.parent or not entity.attachment.binding:
        return []
    parent = session.document.entity(entity.parent)
    key = geometry_asset(parent)
    handle = session.assets[key].mesh.handle if key else 0
    try:
        reference = session.assets.get(entity.attachment.material_asset)
        return anchor_points(
            session.engine, entity, parent, handle, reference.mesh.handle if reference else 0
        )
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
    from .tissue_inspection_scene import picked_rows

    inspected = picked_rows(controller.tissue_inspection, rows)
    controller.display_transforms.retain((*rows, *inspected))
    snapping_inputs(controller, rows)
    eligible = [row for row in inspected if row["surface_pickable"] and row["handle"]]
    controller.pick_rows = {row["id"]: row for row in eligible}
    controller.pick_ids = [row["id"] for row in eligible]
    controller.pick_handles = np.array([row["handle"] for row in eligible], dtype=np.uint64)
    matrices = [
        controller.display_transforms.matrix(controller.session.engine, r) for r in eligible
    ]
    controller.pick_matrices = np.ascontiguousarray(matrices, dtype=np.float64)
    control_picking_inputs(controller)


def displayed_mesh(controller, row):
    from .tissue_inspection_scene import mesh

    return controller.render_model.leases.get(row["handle"]) or mesh(
        controller.tissue_inspection, row
    )


def snapping_inputs(controller, rows):
    eligible = snapping_rows(controller.session.document, rows)
    controller.snap_ids = [row["id"] for row in eligible]
    controller.snap_handles = np.array([row["handle"] for row in eligible], dtype=np.uint64)
    controller.snap_matrices = np.ascontiguousarray(
        [controller.display_transforms.matrix(controller.session.engine, row) for row in eligible],
        dtype=np.float64,
    )


def snapping_rows(document, rows):
    from anthroforge.core.mirroring import source

    anatomy = document.registry.anatomy
    return [
        row
        for row in rows
        if source(row["id"]) in anatomy
        and row["surface_visible"]
        and row["handle"]
        and ready_surface(anatomy[source(row["id"])], row)
    ]


def ready_surface(item, row):
    from anthroforge.core.anatomical_surfaces import usable
    from anthroforge.core.tissues import TissueVCP

    return not isinstance(item, TissueVCP) or (
        usable(item.final_result) and row["geometry_asset"] == item.final_result.asset
    )


def control_picking_inputs(controller):
    eligible = [r for r in controller.markerRows if r["pickable"] and not r["handle"]]
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
    from .section_queries import pick_scene

    hits = pick_scene(controller, origin, direction)
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
    from .image_scene import hits as image_hits
    from .path_scene import hits as path_hits

    hits = mesh_hits(controller, origin, direction) + control_hits(
        controller, origin, direction, radius
    )
    hits += path_hits(controller, origin, direction, radius)
    hits += image_hits(controller, origin, direction)
    hits += controller.construction.points.hits(origin, direction, radius)
    hits.sort(key=lambda hit: (hit.get("layer", 0), hit["distance"]))
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
