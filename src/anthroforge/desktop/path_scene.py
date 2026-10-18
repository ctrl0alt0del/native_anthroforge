"""Native path display and batched picking share the staged displayed revision."""

import numpy as np

from anthroforge.native import paths


def rows(controller):
    resources = controller.session.resources.paths
    return [
        dict(
            row,
            handle=resources[row["asset"]].path.handle,
            geometry_asset=row["asset"],
            chunk=chunk,
            key=f"{row['id']}:{row['asset']}:{chunk}",
        )
        for row in controller.construction.records.values()
        if row["asset"] in resources and row["visible"]
        for chunk in range(resources[row["asset"]].path.chunks)
    ]


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
    return [hit_record(controller.path_ids, row) for row in records]


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
