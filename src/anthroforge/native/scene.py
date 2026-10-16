"""Batch picking and presentation transforms through the same native mesh service."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import GeometryEngine, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    double_pointer = c.POINTER(c.c_double)
    engine.bind("af_quaternion", [double_pointer, double_pointer])
    engine.bind("af_geometry_matrix", [double_pointer, double_pointer, double_pointer])
    engine.bind("af_scene_bounds", [c.c_int, c.POINTER(c.c_uint64), double_pointer, double_pointer])
    configure_picking(engine)


def configure_picking(engine: GeometryEngine) -> None:
    double_pointer = c.POINTER(c.c_double)
    engine.bind(
        "af_scene_pick",
        [
            c.c_int,
            c.POINTER(c.c_uint64),
            double_pointer,
            double_pointer,
            double_pointer,
            double_pointer,
        ],
    )


def quaternion(engine: GeometryEngine, matrix: Any) -> list[float]:
    source, output = doubles(matrix), np.empty(4)
    engine.check(engine.library.af_quaternion(pointer(source), pointer(output)))
    return list(output.tolist())


def geometry_matrix(engine: GeometryEngine, matrix: Any, offset: Any) -> Any:
    source, local, output = doubles(matrix), doubles(offset), np.empty(16)
    engine.check(
        engine.library.af_geometry_matrix(pointer(source), pointer(local), pointer(output))
    )
    return output


def entity_frame(engine: GeometryEngine, entity: Any) -> tuple[float, ...]:
    return tuple(geometry_matrix(engine, entity.matrix, entity.geometry_offset).tolist())


def bounds(engine: GeometryEngine, handles: Any, matrices: Any) -> list[float]:
    meshes, frames = np.ascontiguousarray(handles, dtype=np.uint64), doubles(matrices)
    if frames.size != len(meshes) * 16:
        raise ValueError("Scene bounds require one transform per mesh.")
    output = np.empty(6)
    engine.check(
        engine.library.af_scene_bounds(
            len(meshes),
            meshes.ctypes.data_as(c.POINTER(c.c_uint64)),
            pointer(frames),
            pointer(output),
        )
    )
    return list(output.tolist())


def pick(
    engine: GeometryEngine, handles: Any, matrices: Any, origin: Any, direction: Any
) -> list[Any]:
    output = np.empty((len(handles), 11))
    start, ray = doubles(origin), doubles(direction)
    count = scene_query(engine, handles, matrices, start, ray, output)
    if count < 0:
        engine.check(count)
    return sorted(output[:count].tolist(), key=lambda row: row[1])


def scene_query(
    engine: GeometryEngine, handles: Any, matrices: Any, start: Any, ray: Any, output: Any
) -> int:
    function = engine.library.af_scene_pick
    mesh_pointer = handles.ctypes.data_as(c.POINTER(c.c_uint64))
    return int(
        function(
            len(handles),
            mesh_pointer,
            pointer(matrices),
            pointer(start),
            pointer(ray),
            pointer(output),
        )
    )
