"""Native area-weighted density initialization and budget-preserving log smoothing."""

import ctypes as c
from dataclasses import dataclass
from typing import Any

import numpy as np

from .mesh import D, Mesh, U, doubles, pointer
from .skin_flow import integers


@dataclass(frozen=True)
class Density:
    lengths: Any
    areas: Any
    region_areas: Any
    unusable: Any


def configure(engine: Any) -> None:
    engine.bind("af_skin_proxy_smooth", [U, c.c_double, c.c_int, U], U)
    integer = c.POINTER(c.c_int)
    engine.bind("af_skin_density", [U, integer, D, c.c_int, D, c.c_int, D, D, D, integer, U])


def inputs(mesh: Mesh, regions: Any, budgets: Any, initial: Any) -> tuple[Any, Any, Any]:
    ids, targets = np.ascontiguousarray(regions, dtype=np.int32), doubles(budgets)
    values = None if initial is None else doubles(initial)
    if ids.shape != (mesh.counts[0],) or targets.ndim != 1 or not len(targets):
        raise ValueError("Density needs one region per mesh vertex and exclusive region budgets.")
    if values is not None and values.shape != ids.shape:
        raise ValueError("Initial density lengths must match the mesh vertices.")
    return ids, targets, values


def evaluate(
    mesh: Mesh,
    regions: Any,
    budgets: Any,
    iterations: int = 8,
    initial: Any = None,
    cancel: int = 0,
) -> Density:
    return run(mesh, inputs(mesh, regions, budgets, initial), iterations, cancel)


def run(mesh: Mesh, data: tuple[Any, Any, Any], iterations: int, cancel: int) -> Density:
    ids, targets, initial = data
    lengths, areas, totals = np.empty(len(ids)), np.empty(len(ids)), np.empty(len(targets))
    unusable = np.empty(len(targets), dtype=np.int32)
    args = mesh.handle, integers(ids), pointer(targets), len(targets)
    initial_pointer = None if initial is None else pointer(initial)
    outputs = pointer(lengths), pointer(areas), pointer(totals), integers(unusable)
    mesh.engine.check(
        mesh.engine.library.af_skin_density(*args, initial_pointer, iterations, *outputs, cancel)
    )
    return Density(lengths, areas, totals, unusable)


def smooth_proxy(mesh: Mesh, factor: float = 0.42, iterations: int = 10, cancel: int = 0) -> Mesh:
    handle = mesh.engine.library.af_skin_proxy_smooth(mesh.handle, factor, iterations, cancel)
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)
