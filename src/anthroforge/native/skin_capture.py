"""Batched source transforms and connectivity packing inside the native worker."""

import ctypes as c
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .mesh import INT64, D, GeometryEngine, U, pointer
from .skin_fields import BYTE, INT


def configure(engine: GeometryEngine) -> None:
    engine.bind(
        "af_skin_capture_sources",
        [c.POINTER(U), INT, D, c.c_int, INT, D, D, INT64, INT, BYTE, D, INT64, INT, U],
    )
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
    segments: Any = field(default_factory=lambda: np.empty((0, 2), dtype=np.int64))
    segment_owners: Any = field(default_factory=lambda: np.empty(0, dtype=np.int32))

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


def source_counts(resource: Any, path: bool) -> tuple[int, int, int]:
    if path:
        return resource.count, 0, resource.count - (not resource.closed)
    return resource.counts[0], resource.counts[3], 0


def mixed_outputs(resources: Any, kinds: Any) -> Capture:
    counts = [
        source_counts(resource, kind == 1) for resource, kind in zip(resources, kinds, strict=True)
    ]
    vertices, faces, edges = (sum(row[i] for row in counts) for i in range(3))
    return Capture(
        np.empty((vertices, 3)),
        np.empty((faces, 3), dtype=np.int64),
        np.empty(faces, dtype=np.int32),
        np.empty(faces, dtype=np.uint8),
        np.empty((len(resources), 3)),
        np.empty((edges, 2), dtype=np.int64),
        np.empty(edges, dtype=np.int32),
    )


def capture_sources(
    engine: GeometryEngine, resources: Any, kinds: Any, frames: Any, policies: Any, cancel: int = 0
) -> Capture:
    handles, matrices, rules = inputs(resources, frames, policies)
    kinds = np.ascontiguousarray(kinds, dtype=np.int32)
    if kinds.shape != (len(resources),):
        raise ValueError("Skin source kinds must match resources.")
    result = mixed_outputs(resources, kinds)
    invoke_capture(engine, (handles, kinds, matrices, rules), result, cancel)
    return result


def invoke_capture(engine: GeometryEngine, inputs: Any, result: Capture, cancel: int) -> None:
    handles, kinds, matrices, rules = inputs
    limits = capture_limits(result)
    source = source_arguments(handles, kinds, matrices)
    edges = result.segments.ctypes.data_as(INT64), result.segment_owners.ctypes.data_as(INT)
    arguments = (
        *source,
        limits.ctypes.data_as(INT),
        pointer(rules),
        *result.arguments(),
        *edges,
        cancel,
    )
    engine.check(engine.library.af_skin_capture_sources(*arguments))


def source_arguments(handles: Any, kinds: Any, matrices: Any) -> tuple[Any, ...]:
    return (
        handles.ctypes.data_as(c.POINTER(U)),
        kinds.ctypes.data_as(INT),
        pointer(matrices),
        len(handles),
    )


def capture_limits(result: Capture) -> Any:
    return np.array(
        [len(result.vertices), len(result.triangles), len(result.segments)], dtype=np.int32
    )
