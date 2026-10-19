"""Generic anatomical point capture and resolution, sharing the SCP attachment record."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, GeometryEngine, U, doubles, pointer

INT = c.POINTER(c.c_int)
HANDLES = c.POINTER(U)


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_point_attachment_capture", [c.c_int, HANDLES, D, c.c_int, D, INT, INT, D, U])
    engine.bind("af_point_attachment_resolve", [c.c_int, HANDLES, D, c.c_int, INT, D, D, U])
    engine.bind("af_material_binding_surface", [U, U, c.c_int, D, U], U)


def surface_arrays(meshes: Any, frames: Any) -> tuple[Any, Any]:
    handles, transforms = np.ascontiguousarray(meshes, dtype=np.uint64), doubles(frames)
    if handles.ndim != 1 or transforms.size != len(handles) * 16:
        raise ValueError("Anatomical surfaces need one transform per mesh.")
    return handles, transforms


def capture(
    engine: GeometryEngine,
    meshes: Any,
    frames: Any,
    points: Any,
    forced: Any = None,
    cancel: int = 0,
) -> tuple[Any, Any]:
    surfaces = surface_arrays(meshes, frames)
    positions, choices = capture_inputs(points, forced)
    return capture_owned(engine, surfaces, positions, choices, cancel)


def capture_inputs(points: Any, forced: Any) -> tuple[Any, Any]:
    points = doubles(points)
    choices = (
        np.full(len(points), -1, dtype=np.int32)
        if forced is None
        else np.ascontiguousarray(forced, dtype=np.int32)
    )
    if points.shape != (len(choices), 3) or choices.ndim != 1:
        raise ValueError("Point capture needs xyz rows and optional fixed surface indices.")
    return points, choices


def capture_owned(
    engine: GeometryEngine, surfaces: Any, points: Any, choices: Any, cancel: int
) -> tuple[Any, Any]:
    handles, transforms = surfaces
    targets, bindings = np.empty(len(points), dtype=np.int32), np.empty((len(points), 28))
    prefix = (len(handles), handles.ctypes.data_as(HANDLES), pointer(transforms), len(points))
    args = (pointer(points), choices.ctypes.data_as(INT), targets.ctypes.data_as(INT))
    engine.check(
        engine.library.af_point_attachment_capture(*prefix, *args, pointer(bindings), cancel)
    )
    return targets, bindings


def resolve(
    engine: GeometryEngine, meshes: Any, frames: Any, targets: Any, bindings: Any, cancel: int = 0
) -> Any:
    handles, transforms = surface_arrays(meshes, frames)
    targets, bindings = np.ascontiguousarray(targets, dtype=np.int32), doubles(bindings)
    if targets.ndim != 1 or bindings.shape != (len(targets), 28):
        raise ValueError("Point resolution needs targets and captured attachment records.")
    output = np.empty((len(targets), 16))
    prefix = (len(handles), handles.ctypes.data_as(HANDLES), pointer(transforms), len(targets))
    engine.check(
        engine.library.af_point_attachment_resolve(
            *prefix, targets.ctypes.data_as(INT), pointer(bindings), pointer(output), cancel
        )
    )
    return output
