"""Batched local displacement and explicit mesh subdivision stages."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, GeometryEngine, Mesh, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_simple_subdivision", [U, c.c_int, U], U)
    engine.bind("af_displace", [D, c.c_int, D, D, c.c_int, c.c_double, D, U])


def subdivide(mesh: Mesh, levels: int, cancel: int = 0) -> Mesh:
    if not levels:
        return mesh
    handle = mesh.engine.library.af_simple_subdivision(mesh.handle, levels, cancel)
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)


def displace(engine: GeometryEngine, points: Any, binding: Any, cancel: int = 0) -> Any:
    source = doubles(points)
    offset, weights = doubles(binding.displacement), doubles(binding.weights)
    if weights.size not in (0, len(source)):
        raise ValueError("Displacement weights must match the input vertices.")
    output = np.empty_like(source)
    evaluate_displacement(engine, source, offset, weights, binding, output, cancel)
    return output


def evaluate_displacement(
    engine: Any, source: Any, offset: Any, weights: Any, binding: Any, output: Any, cancel: int
) -> None:
    inputs = (
        pointer(source),
        len(source),
        pointer(offset),
        pointer(weights) if len(weights) else None,
    )
    engine.check(
        engine.library.af_displace(
            *inputs, binding.invert, binding.strength, pointer(output), cancel
        )
    )
