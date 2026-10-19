"""Pack frozen donor arrays without introducing application-side numerical computation."""

import numpy as np

from anthroforge.native import stacking_abi as abi
from anthroforge.native.mesh import INT64, pointer


def arrays(record, names, integer=False):
    return {
        name: np.ascontiguousarray(record[name], dtype=np.int64 if integer else float)
        for name in names
    }


def material(record):
    buffers = arrays(record, ("vertices", "weights", "constraint_weights"))
    buffers.update(arrays(record, ("faces", "interpolation", "fixed", "constraints"), True))
    row = abi.Material()
    assign_buffers(row, buffers)
    row.vertices_count, row.faces_count = len(buffers["vertices"]), len(buffers["faces"])
    row.samples, row.width = buffers["interpolation"].shape
    row.fixed_count, row.constraint_count = len(buffers["fixed"]), len(buffers["constraints"])
    return row, buffers


def assign_buffers(row, buffers):
    for key, value in buffers.items():
        setattr(
            row, key, value.ctypes.data_as(INT64) if value.dtype.kind == "i" else pointer(value)
        )


def domain(record):
    row = abi.Domain()
    buffers = arrays(record, ("base", "own", "direction"))
    buffers.update(arrays(record, ("faces", "parts", "sources"), True))
    assign_buffers(row, buffers)
    for key in ("id", "family", "root", "enabled", "side", "allowance"):
        setattr(row, key, record[key])
    row.vertices, row.triangles = len(buffers["base"]), len(buffers["faces"])
    row.material, backing = material(record["material"])
    return row, (buffers, backing)


def settings(record):
    stack = record["stacking"]
    detection = [record[k] for k in ("search_distance", "min_projected_area", "epsilon")]
    names = (
        "clearance",
        "radius",
        "strength",
        "blend_distance",
        "preservation_weight",
        "smoothing_max_adjustment",
    )
    budgets = [record[k] for k in ("cache_bytes", "result_bytes", "fragment_limit")]
    return abi.Settings(*detection, *(stack[k] for k in names), *budgets)


def obstacles(records):
    packed = []
    for record in records:
        vertices = np.ascontiguousarray(record["vertices"], dtype=float)
        faces = np.ascontiguousarray(record["faces"], dtype=np.int64)
        row = abi.Obstacle(
            pointer(vertices), faces.ctypes.data_as(INT64), len(vertices), len(faces)
        )
        packed.append((row, (vertices, faces)))
    return packed


def options(case):
    bones = obstacles(case.get("obstacles", ()))
    values = dict(
        policies=[abi.Policy(**p) for p in case.get("policies", ())],
        regions=case.get("regions", ()),
        obstacles=[row[0] for row in bones],
    )
    return values, bones
