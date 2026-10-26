"""Native guide transitions; returned topology owns its geometry and provenance."""

import ctypes as c
from dataclasses import dataclass
from typing import Any

import numpy as np

from . import skin_topology
from .mesh import D, Mesh, U, doubles, pointer
from .skin_annuli import Annuli


class Input(c.Structure):
    _fields_ = [
        ("first", D),
        ("second", D),
        ("plane", D),
        ("first_count", c.c_int),
        ("second_count", c.c_int),
        ("diagonal", c.c_double),
    ]


@dataclass(frozen=True)
class Transition:
    topology: skin_topology.Result
    diagnostics: Any


class Output(c.Structure):
    _fields_ = [
        ("transitions", D),
        ("capacity", c.c_int),
        ("count", c.c_int),
        ("warning", c.POINTER(c.c_char)),
        ("warning_capacity", c.c_int),
    ]


@dataclass(frozen=True)
class Assembly:
    topology: skin_topology.Result
    transitions: Any
    warning: str


def configure(engine: Any) -> None:
    engine.bind("af_skin_transition", [c.POINTER(Input), D, U], U)
    engine.bind("af_skin_stitch", [U, U, D, c.c_int, c.POINTER(Output), U], U)


def inputs(first: Any, second: Any, plane: Any) -> tuple[Any, Any, Any]:
    a, b = doubles(first), doubles(second)
    frame = None if plane is None else doubles(plane)
    if any(row.ndim != 2 or row.shape[1] != 3 for row in (a, b)):
        raise ValueError("Skin transition boundaries require XYZ arrays.")
    if frame is not None and frame.shape != (6,):
        raise ValueError("Skin transition symmetry requires a six-component plane.")
    return a, b, frame


def build(
    engine: Any, first: Any, second: Any, diagonal: float, plane: Any = None, cancel: int = 0
) -> Transition:
    a, b, frame = inputs(first, second, plane)
    source = Input(
        pointer(a), pointer(b), None if frame is None else pointer(frame), len(a), len(b), diagonal
    )
    report = np.empty(9)
    handle = engine.library.af_skin_transition(c.byref(source), pointer(report), cancel)
    return Transition(skin_topology.consume(engine, handle), report)


def assembly_buffers(annuli: Annuli, plane: Any) -> tuple[Any, ...]:
    count = annuli.counts[2]
    reports = np.empty((count, 9))
    warning = c.create_string_buffer(4096)
    output = Output(pointer(reports), count, 0, warning, len(warning))
    frame = None if plane is None else doubles(plane)
    if frame is not None and frame.shape != (6,):
        raise ValueError("Skin assembly symmetry requires a six-component plane.")
    return reports, warning, output, frame


def assemble(
    mesh: Mesh, annuli: Annuli, plane: Any = None, allow_unstitched: bool = False, cancel: int = 0
) -> Assembly:
    if mesh.engine is not annuli.engine:
        raise ValueError("Skin assembly inputs must use one geometry engine.")
    reports, warning, output, frame = assembly_buffers(annuli, plane)
    args = mesh.handle, annuli.handle, None if frame is None else pointer(frame)
    handle = mesh.engine.library.af_skin_stitch(
        *args, int(allow_unstitched), c.byref(output), cancel
    )
    topology = skin_topology.consume(mesh.engine, handle)
    return Assembly(topology, reports[: output.count], warning.value.decode("utf-8"))
