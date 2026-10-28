"""Native path display and batched picking share the staged displayed revision."""

import numpy as np

from anthroforge.native import paths

from .inspection_visibility import records


def rows(controller):
    from .mirror_scene import path_rows

    return path_rows(controller, source_rows(controller))


def source_rows(controller):
    resources = controller.session.resources.paths
    return [
        dict(
            row,
            handle=resources[row["asset"]].path.handle,
            geometry_asset=row["asset"],
            chunk=chunk,
            key=f"{row['id']}:{row['asset']}:{chunk}",
        )
        for row in records(controller, controller.construction.records.values())
        if row["asset"] in resources and row["visible"] and not row.get("fiber_radius", 0)
        for chunk in range(resources[row["asset"]].path.chunks)
    ]


def resources(controller):
    yield from (asset.path for asset in controller.session.resources.paths.values())
    if controller.session.conversion.asset is not None:
        yield controller.session.conversion.asset.path


def preview_rows(controller):
    from anthroforge.application.curve_conversion import current

    from .mirror_scene import previews

    value = controller.session.conversion
    source = controller.construction.records.get(value.target)
    if not source or not current(controller.session, value):
        return []
    if value.state != "ready" or value.asset is None:
        return []
    rows = [preview_record(source, value, chunk) for chunk in range(value.asset.path.chunks)]
    return previews(controller, rows, value.target)


def preview_record(source, value, chunk):
    return dict(
        source,
        id="preview:" + value.token,
        key=f"preview:{value.token}:{chunk}",
        handle=value.asset.path.handle,
        geometry_asset=value.token,
        chunk=chunk,
        pickable=False,
        readonly=False,
        preview=True,
    )


def prepare_picking(controller):
    displayed = controller.path_model.active_rows()
    eligible = [row for row in displayed if row["pickable"] and row["visible"]]
    controller.path_ids = [row["id"] for row in eligible]
    controller.path_handles = np.array([row["handle"] for row in eligible], dtype=np.uint64)
    controller.path_matrices = np.ascontiguousarray([row["matrix"] for row in eligible])


def hits(controller, origin, direction, radius):
    records = paths.pick(
        controller.session.engine,
        controller.path_handles,
        controller.path_matrices,
        origin,
        direction,
        radius,
    )
    return [
        hit_record(controller.path_ids, row) for row in records
    ] + controller.fiber_display.hits(origin, direction)


def hit_record(ids, row):
    return dict(
        id=ids[int(row[0])],
        distance=row[1],
        segment=int(row[2]),
        point=row[3:6].tolist(),
        face=-1,
        triangle=-1,
        vertex=-1,
    )
