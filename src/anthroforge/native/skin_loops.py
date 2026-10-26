"""Batched closed-guide projection/pairing, independent of authored paths and presentation."""

import ctypes as c
from dataclasses import dataclass
from typing import Any

import numpy as np

from .mesh import D, Mesh, U, doubles, pointer
from .skin_flow import integers

INT = c.POINTER(c.c_int)


class Input(c.Structure):
    _fields_ = [("paths", c.POINTER(U)), ("frames", D), ("plane", D), ("count", c.c_int)]


class Output(c.Structure):
    _fields_ = [
        ("samples", D),
        ("sources", INT),
        ("pairs", INT),
        ("statuses", INT),
        ("symmetric", INT),
        ("sizes", INT),
    ]


@dataclass(frozen=True)
class Loops:
    samples: Any
    sources: Any
    pairs: Any
    statuses: Any
    symmetric: Any


def configure(engine: Any) -> None:
    engine.bind("af_skin_loops", [U, c.POINTER(Input), c.POINTER(Output), U])


def inputs(mesh: Mesh, paths: Any, frames: Any, plane: Any) -> tuple[Any, Any, Any]:
    if len(paths) > 2048 or any(path.engine is not mesh.engine for path in paths):
        raise ValueError("Skin loop sources must use one engine and at most 2048 paths.")
    ids = np.array([path.handle for path in paths], dtype=np.uint64)
    matrices = doubles(frames)
    equation = None if plane is None else doubles(plane)
    if matrices.size != len(paths) * 16 or (equation is not None and equation.size != 6):
        raise ValueError("Skin loops require one frame per path and an optional six-value plane.")
    return ids, matrices, equation


def prepare(mesh: Mesh, paths: Any, frames: Any, plane: Any = None, cancel: int = 0) -> Loops:
    return evaluate(mesh, inputs(mesh, paths, frames, plane), cancel)


def evaluate(mesh: Mesh, packed: Any, cancel: int) -> Loops:
    ids, frames, plane = packed
    source = Input(
        ids.ctypes.data_as(c.POINTER(U)),
        pointer(frames),
        None if plane is None else pointer(plane),
        len(ids),
    )
    arrays = buffers(len(ids))
    output = Output(pointer(arrays[0]), *(integers(value) for value in arrays[1:]))
    mesh.engine.check(
        mesh.engine.library.af_skin_loops(mesh.handle, c.byref(source), c.byref(output), cancel)
    )
    return result(arrays)


def result(arrays: Any) -> Loops:
    samples, sources, pairs, statuses, symmetric, sizes = arrays
    return Loops(
        samples[: sizes[0]], sources[: sizes[0]], pairs[: sizes[1]], statuses, symmetric[: sizes[0]]
    )


def buffers(count: int) -> tuple[Any, ...]:
    return (
        np.empty((count, 192, 6)),
        np.empty(count, dtype=np.int32),
        np.empty((count, 2), dtype=np.int32),
        np.empty(count, dtype=np.int32),
        np.empty(count, dtype=np.int32),
        np.empty(2, dtype=np.int32),
    )
