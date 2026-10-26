"""Owned topology bundles and native conforming all-quad refinement."""

import ctypes as c
from dataclasses import dataclass
from typing import Any

import numpy as np

from .mesh import D, Mesh, U, pointer
from .skin_fields import BYTE, INT
from .skin_flow import integers


@dataclass(frozen=True)
class Result:
    mesh: Mesh
    regions: Any
    guides: Any


def configure(engine: Any) -> None:
    engine.bind("af_skin_quads_split", [U, BYTE, INT, INT, U], U)
    engine.bind("af_skin_refine", [U, U, D, INT, INT, c.c_int, c.c_int, D, U], U)
    engine.bind("af_skin_topology_mesh", [U], U)
    engine.bind("af_skin_topology_labels", [U, INT, INT, c.c_int])
    engine.bind("af_skin_topology_release", [U], None)


def labels(mesh: Any, regions: Any, guides: Any) -> tuple[Any, Any]:
    count = mesh.counts[1]
    regions = np.zeros(count, dtype=np.int32) if regions is None else np.asarray(regions)
    guides = np.full(count, -1, dtype=np.int32) if guides is None else np.asarray(guides)
    if regions.shape != (count,) or guides.shape != (count,):
        raise ValueError("Topology labels must match polygons.")
    return np.ascontiguousarray(regions, dtype=np.int32), np.ascontiguousarray(
        guides, dtype=np.int32
    )


def consume(engine: Any, handle: int) -> Result:
    engine.check(not handle)
    try:
        resource = engine.library.af_skin_topology_mesh(handle)
        engine.check(not resource)
        mesh = Mesh(engine, resource)
        regions, guides = labels(mesh, None, None)
        engine.check(
            engine.library.af_skin_topology_labels(
                handle, integers(regions), integers(guides), mesh.counts[1]
            )
        )
        return Result(mesh, regions, guides)
    finally:
        engine.library.af_skin_topology_release(handle)


def split(
    mesh: Any, selected: Any, regions: Any = None, guides: Any = None, cancel: int = 0
) -> Result:
    ids, refs = labels(mesh, regions, guides)
    mask = np.ascontiguousarray(selected, dtype=np.uint8)
    if mask.shape != (mesh.counts[1],):
        raise ValueError("Refinement selection must match polygons.")
    args = mesh.handle, mask.ctypes.data_as(BYTE), integers(ids), integers(refs), cancel
    return consume(mesh.engine, mesh.engine.library.af_skin_quads_split(*args))


def refinement_inputs(mesh: Any, density: Any, lengths: Any, plane: Any) -> tuple[Any, Any]:
    values = np.ascontiguousarray(lengths, dtype=np.float64)
    frame = None if plane is None else np.ascontiguousarray(plane, dtype=np.float64)
    if values.shape != (density.counts[0],) or (frame is not None and frame.shape != (6,)):
        raise ValueError("Refinement needs density lengths and an optional six-component plane.")
    if mesh.engine is not density.engine:
        raise ValueError("Refinement resources must belong to the same engine.")
    return values, frame


def refine(
    mesh: Any,
    density: Any,
    lengths: Any,
    target: int,
    regions: Any = None,
    guides: Any = None,
    plane: Any = None,
    passes: int = 2,
    cancel: int = 0,
) -> Result:
    data = refinement_inputs(mesh, density, lengths, plane)
    return run_refinement(
        mesh, density, data, labels(mesh, regions, guides), target, passes, cancel
    )


def run_refinement(
    mesh: Any, density: Any, data: Any, provenance: Any, target: int, passes: int, cancel: int
) -> Result:
    values, frame = data
    ids, refs = provenance
    args = mesh.handle, density.handle, pointer(values), integers(ids), integers(refs)
    normal = None if frame is None else pointer(frame)
    handle = mesh.engine.library.af_skin_refine(*args, target, passes, normal, cancel)
    return consume(mesh.engine, handle)
