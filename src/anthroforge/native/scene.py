"""Batch picking and presentation transforms through the same native mesh service."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import GeometryEngine, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    double_pointer = c.POINTER(c.c_double)
    engine.bind("af_quaternion", [double_pointer, double_pointer])
    engine.bind("af_axis_rotation", [double_pointer, c.c_double, double_pointer])
    engine.bind("af_surface_normal", [c.c_uint64, double_pointer, c.c_int, double_pointer])
    engine.bind(
        "af_surface_snap",
        [c.c_uint64, double_pointer, c.c_int, double_pointer, c.c_double, double_pointer],
    )
    engine.bind("af_geometry_matrix", [double_pointer, double_pointer, double_pointer])
    engine.bind("af_scene_bounds", [c.c_int, c.POINTER(c.c_uint64), double_pointer, double_pointer])
    engine.bind("af_bounds_union", [c.c_int, double_pointer, double_pointer, double_pointer])
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


def axis_rotation(engine: GeometryEngine, axis: Any, angle: float) -> list[float]:
    source, output = doubles(axis), np.empty(3)
    engine.check(engine.library.af_axis_rotation(pointer(source), angle, pointer(output)))
    return list(output.tolist())


def surface_normal(engine: GeometryEngine, handle: int, matrix: Any, triangle: int) -> list[float]:
    frame, output = doubles(matrix), np.empty(3)
    engine.check(
        engine.library.af_surface_normal(handle, pointer(frame), triangle, pointer(output))
    )
    return list(output.tolist())


def surface_snap(
    engine: GeometryEngine,
    handle: int,
    matrix: Any,
    triangle: int,
    position: Any,
    offset: float = 0.0,
) -> dict[str, Any]:
    frame, start, output = snap_buffers(matrix, position)
    engine.check(
        engine.library.af_surface_snap(
            handle, pointer(frame), triangle, pointer(start), offset, pointer(output)
        )
    )
    return dict(point=output[:3].tolist(), normal=output[3:6].tolist(), clearance=float(output[6]))


def snap_buffers(matrix: Any, position: Any) -> tuple[Any, Any, Any]:
    frame, start = doubles(matrix), doubles(position)
    if frame.size != 16 or start.size != 3:
        raise ValueError("Surface snapping needs a transform and a world point.")
    return frame, start, np.empty(7)


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


def boxes(engine: GeometryEngine, bounds: Any, matrices: Any) -> list[float]:
    values, frames = doubles(bounds), doubles(matrices)
    if values.ndim != 2 or values.shape[1] != 6 or frames.size != len(values) * 16:
        raise ValueError("Bounds require one six-value box and transform per object.")
    output = np.empty(6)
    engine.check(
        engine.library.af_bounds_union(
            len(values), pointer(values), pointer(frames), pointer(output)
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
