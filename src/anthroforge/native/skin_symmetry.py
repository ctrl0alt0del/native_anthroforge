"""Owned symmetry preparation shared by both skin remeshing backends."""

import ctypes as c
from dataclasses import replace
from typing import Any

import numpy as np

from . import skin_topology
from .mesh import D, Mesh, U, doubles, pointer
from .skin_guide_batch import Input, buffers, record
from .skin_guides import Guides, consume


def configure(engine: Any) -> None:
    engine.bind("af_skin_symmetry_half", [U, D, U], U)
    engine.bind("af_skin_symmetry_mirror", [U, D, U], U)
    engine.bind("af_skin_guides_half", [c.POINTER(Input), D, U], U)
    engine.bind("af_skin_symmetry_plane", [D, D, D])


def world_plane(engine: Any, matrix: Any, plane: Any) -> Any:
    frame, local = doubles(matrix), equation(plane)
    if frame.shape not in ((16,), (4, 4)):
        raise ValueError("Skin symmetry needs a four-by-four root transform.")
    output = np.empty(6)
    engine.check(
        engine.library.af_skin_symmetry_plane(pointer(frame), pointer(local), pointer(output))
    )
    return output


def equation(plane: Any) -> Any:
    value = doubles(plane)
    if value.shape != (6,):
        raise ValueError("Skin symmetry needs a six-component plane.")
    return value


def half(mesh: Mesh, plane: Any, cancel: int = 0) -> Mesh:
    value = equation(plane)
    handle = mesh.engine.library.af_skin_symmetry_half(mesh.handle, pointer(value), cancel)
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)


def mirror(mesh: Mesh, plane: Any, cancel: int = 0) -> skin_topology.Result:
    value = equation(plane)
    handle = mesh.engine.library.af_skin_symmetry_mirror(mesh.handle, pointer(value), cancel)
    return skin_topology.consume(mesh.engine, handle)


def guides(engine: Any, source: Guides, plane: Any, cancel: int = 0) -> Guides:
    values, frame = buffers(source), equation(plane)
    input = record(values)
    handle = engine.library.af_skin_guides_half(c.byref(input), pointer(frame), cancel)
    return replace(consume(engine, handle), regions=source.regions)
