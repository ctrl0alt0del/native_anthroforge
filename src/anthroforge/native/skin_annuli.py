"""Owned annular guide patches; construction and candidate selection stay native."""

import ctypes as c
from dataclasses import dataclass
from typing import Any

import numpy as np

from .mesh import INT64, D, Mesh, U, doubles, pointer
from .skin_flow import integers
from .skin_loops import INT, Loops


class Input(c.Structure):
    _fields_ = [
        ("samples", D),
        ("pairs", INT),
        ("symmetric", INT),
        ("plane", D),
        ("loop_count", c.c_int),
        ("pair_count", c.c_int),
    ]


@dataclass(frozen=True)
class Snapshot:
    samples: Any
    quads: Any
    patches: Any


def configure(engine: Any) -> None:
    engine.bind("af_skin_annuli", [U, c.POINTER(Input), U], U)
    engine.bind("af_skin_annuli_sizes", [U, INT])
    engine.bind("af_skin_annuli_copy", [U, D, INT64, INT, INT])
    engine.bind("af_skin_annuli_release", [U], None)
    engine.bind("af_skin_cut_guides", [U, U, D, U], U)


class Annuli:
    def __init__(self, engine: Any, handle: int) -> None:
        engine.check(not handle)
        self.engine, self.handle = engine, handle

    def close(self) -> None:
        if self.handle:
            self.engine.library.af_skin_annuli_release(self.handle)
            self.handle = 0

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.close()

    def snapshot(self) -> Snapshot:
        sizes = np.empty(3, dtype=np.int32)
        self.engine.check(self.engine.library.af_skin_annuli_sizes(self.handle, integers(sizes)))
        samples = np.empty((sizes[0], 6))
        quads = np.empty((sizes[1], 4), dtype=np.int64)
        patches = np.empty((sizes[2], 9), dtype=np.int32)
        args = self.handle, pointer(samples), quads.ctypes.data_as(INT64)
        self.engine.check(
            self.engine.library.af_skin_annuli_copy(*args, integers(patches), integers(sizes))
        )
        return Snapshot(samples, quads, patches)


def inputs(loops: Loops, plane: Any) -> tuple[Any, ...]:
    samples = doubles(loops.samples)
    pairs = np.ascontiguousarray(loops.pairs, dtype=np.int32)
    symmetric = np.ascontiguousarray(loops.symmetric, dtype=np.int32)
    equation = None if plane is None else doubles(plane)
    if samples.ndim != 3 or samples.shape[1:] != (192, 6):
        raise ValueError("Annulus guides require 192 position/normal samples per loop.")
    if pairs.ndim != 2 or pairs.shape[1] != 2 or symmetric.shape != (len(samples),):
        raise ValueError("Annulus pairs and symmetry must match captured guides.")
    if equation is not None and equation.shape != (6,):
        raise ValueError("Annulus symmetry requires a six-component plane.")
    return samples, pairs, symmetric, equation


def build(mesh: Mesh, loops: Loops, plane: Any = None, cancel: int = 0) -> Annuli:
    samples, pairs, symmetric, equation = inputs(loops, plane)
    source = Input(
        pointer(samples),
        integers(pairs),
        integers(symmetric),
        None if equation is None else pointer(equation),
        len(samples),
        len(pairs),
    )
    handle = mesh.engine.library.af_skin_annuli(mesh.handle, c.byref(source), cancel)
    return Annuli(mesh.engine, handle)


def cut_guides(mesh: Mesh, annuli: Annuli, plane: Any = None, cancel: int = 0) -> Mesh:
    equation = None if plane is None else doubles(plane)
    if equation is not None and equation.shape != (6,):
        raise ValueError("Guide cut symmetry requires a six-component plane.")
    if mesh.engine is not annuli.engine:
        raise ValueError("Guide cuts require one geometry engine.")
    args = mesh.handle, annuli.handle, None if equation is None else pointer(equation), cancel
    handle = mesh.engine.library.af_skin_cut_guides(*args)
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)
