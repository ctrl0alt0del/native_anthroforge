"""Owned native preparation and sparse shape reconstruction for fiber propagation."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, GeometryEngine, U, doubles, pointer
from .point_attachments import HANDLES, INT, surface_arrays


class Reference(c.Structure):
    _fields_ = [
        ("path", U),
        ("records", D),
        ("controls", c.c_int),
        ("world", D),
        ("owners", INT),
        ("weights", D),
        ("bindings", D),
        ("surfaces", c.c_int),
        ("meshes", HANDLES),
        ("frames", D),
        ("pins", c.c_int),
        ("indices", INT),
        ("groups", INT),
        ("hints", D),
    ]


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_fiber_deformation_prepare", [c.POINTER(Reference), U], U)
    engine.bind("af_fiber_deformation_evaluate", [U, HANDLES, D, D, D, U])
    engine.bind("af_fiber_deformation_bytes", [U], U)
    engine.bind("af_fiber_deformation_release", [U], None)


class Preparation:
    def __init__(
        self, engine: GeometryEngine, field: Any, meshes: Any, pins: Any, groups: Any, cancel: int
    ):
        self.engine, self.field, self.meshes = engine, field, tuple(meshes)
        self.handle = create(engine, field, meshes, pins, groups, cancel)

    @property
    def bytes(self) -> int:
        native = int(self.engine.library.af_fiber_deformation_bytes(self.handle))
        return int(native + self.field.bytes + self.field.path.bytes)

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_fiber_deformation_release(self.handle)


def create(
    engine: GeometryEngine, field: Any, meshes: Any, pins: Any, groups: Any, cancel: int
) -> int:
    frames = field.frames or ((0.0,) * 16,) * len(meshes)
    handles, matrices = surface_arrays([m.handle for m in meshes], frames)
    indices, world = np.ascontiguousarray(pins, dtype=np.int32), doubles(field.world)
    groups = np.ascontiguousarray(groups, dtype=np.int32)
    hints = doubles(field.frame_hints or ((0.0,) * 16,) * len(meshes))
    value = Reference(
        *field_arguments(field, world),
        *surface_arguments(handles, matrices, indices, groups, hints),
    )
    handle = engine.library.af_fiber_deformation_prepare(c.byref(value), cancel)
    engine.check(not handle)
    return int(handle)


def field_arguments(field: Any, world: Any) -> Any:
    return (
        field.path.handle,
        pointer(field.records),
        len(field.records),
        pointer(world),
        field.owners.ctypes.data_as(INT),
        pointer(field.weights),
        pointer(field.bindings),
    )


def surface_arguments(handles: Any, matrices: Any, indices: Any, groups: Any, hints: Any) -> Any:
    return (
        len(handles),
        handles.ctypes.data_as(HANDLES),
        pointer(matrices),
        len(indices),
        indices.ctypes.data_as(INT),
        groups.ctypes.data_as(INT),
        pointer(hints),
    )


def prepare(
    engine: GeometryEngine, field: Any, meshes: Any, pins: Any, groups: Any, cancel: int
) -> Preparation:
    key = (field, tuple(m.handle for m in meshes), tuple(pins), tuple(groups))
    found = engine.fiber_deformations.get(key)
    if found is not None:
        return found
    value = Preparation(engine, field, meshes, pins, groups, cancel)
    return engine.fiber_deformations.store(key, value, value.bytes)


def evaluate(value: Preparation, handles: Any, frames: Any, goals: Any, cancel: int) -> Any:
    meshes, matrices = surface_arrays(handles, frames)
    goals = doubles(goals)
    output = np.empty((len(value.field.owners), 3))
    value.engine.check(
        value.engine.library.af_fiber_deformation_evaluate(
            value.handle,
            meshes.ctypes.data_as(HANDLES),
            pointer(matrices),
            pointer(goals),
            pointer(output),
            cancel,
        )
    )
    return output
