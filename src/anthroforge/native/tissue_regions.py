"""Native material face lookup and footprint outlines over displayed geometry."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import INT64, D, GeometryEngine, Mesh, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_tissue_region_face", [U, c.c_int64, c.c_int, INT64])
    engine.bind("af_tissue_regions_check", [U, INT64, c.c_int, c.c_int])
    engine.bind("af_tissue_region_lines", [U, INT64, c.c_int, c.c_int, D, D, c.c_int64], c.c_int64)


def face(mesh: Mesh, polygon: int, side: str) -> tuple[int, int] | None:
    output = (c.c_int64 * 2)()
    code = mesh.engine.library.af_tissue_region_face(
        mesh.handle, polygon, 1 + (side == "b"), output
    )
    mesh.engine.check(code < 0)
    return (output[0], output[1]) if code else None


def packed(regions: Any) -> Any:
    return np.ascontiguousarray(regions, dtype=np.int64).reshape((-1, 2))


def validate(mesh: Mesh, regions: Any, side: str) -> None:
    values = packed(regions)
    mesh.engine.check(
        mesh.engine.library.af_tissue_regions_check(
            mesh.handle, values.ctypes.data_as(INT64), len(values), 1 + (side == "b")
        )
    )


def lines(mesh: Mesh, regions: Any, side: str, frame: Any) -> Any:
    values, matrix = packed(regions), doubles(frame)
    args = (
        mesh.handle,
        values.ctypes.data_as(INT64),
        len(values),
        1 + (side == "b"),
        pointer(matrix),
    )
    method = mesh.engine.library.af_tissue_region_lines
    count = method(*args, None, 0)
    mesh.engine.check(count < 0)
    output = np.empty(count, dtype=np.float64)
    mesh.engine.check(method(*args, pointer(output), count) < 0)
    return output.reshape((-1, 3))
