"""Native guide transitions; returned topology owns its geometry and provenance."""

import ctypes as c
from dataclasses import dataclass
from typing import Any

import numpy as np

from . import skin_topology
from .mesh import D, U, doubles, pointer


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


def configure(engine: Any) -> None:
    engine.bind("af_skin_transition", [c.POINTER(Input), D, U], U)


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
