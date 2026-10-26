"""Batched source transforms and connectivity packing inside the native worker."""

import ctypes as c
from dataclasses import dataclass
from typing import Any

import numpy as np

from .mesh import INT64, D, GeometryEngine, U, pointer
from .skin_fields import BYTE, INT


def configure(engine: GeometryEngine) -> None:
    engine.bind(
        "af_skin_capture",
        [c.POINTER(U), D, c.c_int, c.c_int, c.c_int, D, D, INT64, INT, BYTE, D, U],
    )


@dataclass(frozen=True)
class Capture:
    vertices: Any
    triangles: Any
    owners: Any
    skeletal: Any
    policies: Any

    def arguments(self) -> tuple[Any, ...]:
        return (
            pointer(self.vertices),
            self.triangles.ctypes.data_as(INT64),
            self.owners.ctypes.data_as(INT),
            self.skeletal.ctypes.data_as(BYTE),
            pointer(self.policies),
        )


def outputs(meshes: Any) -> Capture:
    vertices = sum(mesh.counts[0] for mesh in meshes)
    triangles = sum(mesh.counts[3] for mesh in meshes)
    return Capture(
        np.empty((vertices, 3)),
        np.empty((triangles, 3), dtype=np.int64),
        np.empty(triangles, dtype=np.int32),
        np.empty(triangles, dtype=np.uint8),
        np.empty((len(meshes), 3)),
    )


def inputs(meshes: Any, frames: Any, policies: Any) -> tuple[Any, ...]:
    handles = np.ascontiguousarray([mesh.handle for mesh in meshes], dtype=np.uint64)
    matrices, rules = (
        np.ascontiguousarray(value, dtype=np.float64) for value in (frames, policies)
    )
    if matrices.shape != (len(meshes), 16) or rules.shape != (len(meshes), 3) or not len(meshes):
        raise ValueError("Skin capture needs geometry, a transform and policy per source.")
    return handles, matrices, rules


def capture(
    engine: GeometryEngine, meshes: Any, frames: Any, policies: Any, cancel: int = 0
) -> Capture:
    handles, matrices, rules = inputs(meshes, frames, policies)
    result = outputs(meshes)
    source = handles.ctypes.data_as(c.POINTER(U)), pointer(matrices), len(meshes)
    counts = len(result.vertices), len(result.triangles)
    engine.check(
        engine.library.af_skin_capture(
            *source, *counts, pointer(rules), *result.arguments(), cancel
        )
    )
    return result
