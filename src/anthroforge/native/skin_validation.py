"""Advisory topology observations; invalid quality never becomes an implicit repair."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, U, doubles, pointer
from .skin_flow import integers

FIELDS = (
    "finite",
    "all_quads",
    "components",
    "orientable",
    "manifold",
    "no_degenerates",
    "boundary_loops",
    "boundary_match",
    "guide_preserved",
    "symmetry_error",
    "symmetry_ok",
    "fidelity_p95",
    "fidelity_ok",
    "max_valence",
    "valence_ok",
    "degenerate_faces",
)


def configure(engine: Any) -> None:
    engine.bind("af_skin_topology_quality", [U, U, c.POINTER(c.c_int), c.c_int, c.c_int, D, D, U])


def inputs(result: Any, envelope: Any, plane: Any) -> Any:
    mesh = result.mesh
    ids = np.ascontiguousarray(result.regions, dtype=np.int32)
    frame = None if plane is None else doubles(plane)
    if mesh.engine is not envelope.engine or ids.shape != (mesh.counts[1],):
        raise ValueError("Topology diagnostics require shared engine and polygon region labels.")
    if frame is not None and frame.shape != (6,):
        raise ValueError("Topology diagnostics require a six-component symmetry plane.")
    return ids, frame


def evaluate(
    result: Any, envelope: Any, guide_faces: int, patches: int, plane: Any = None, cancel: int = 0
) -> dict[str, Any]:
    mesh = result.mesh
    ids, frame = inputs(result, envelope, plane)
    args = mesh.handle, envelope.handle, integers(ids), guide_faces, patches
    values = np.empty(16)
    normal = None if frame is None else pointer(frame)
    mesh.engine.check(
        mesh.engine.library.af_skin_topology_quality(*args, normal, pointer(values), cancel)
    )
    return dict(zip(FIELDS, values.tolist(), strict=True)) | dict(self_intersections=None)
