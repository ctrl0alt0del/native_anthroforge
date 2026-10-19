"""Leased native tissue stacking preparation and complete mesh assembly."""

import ctypes as c
from typing import Any

from .mesh import INT64, D, U
from .stacking_abi import Domain
from .tissue_inflation import Inflation
from .tissue_relaxation import Region, Settings


class Source(c.Structure):
    _fields_ = [(name, U) for name in ("base", "rest", "own")]
    _fields_ += [("frame", c.c_double * 16), ("crop", c.c_double * 7)]
    _fields_ += [(name, c.c_int) for name in ("cropped", "side", "reverse")]
    _fields_ += [("inflation", c.POINTER(Inflation)), ("parts", c.c_int)]
    _fields_ += [
        ("relaxation", Settings),
        ("regions", c.POINTER(Region)),
        ("region_count", c.c_int),
    ]
    _fields_ += [("pins", INT64), ("pin_weights", D), ("pin_count", c.c_int)]


def configure(engine: Any) -> None:
    engine.bind("af_tissue_stack_prepare", [c.POINTER(Source), U], U)
    engine.bind("af_tissue_stack_release", [U], None)
    engine.bind("af_tissue_stack_domain", [U, c.POINTER(Domain)])
    engine.bind("af_tissue_stack_apply", [U, U, D, c.c_int, D, c.c_int, U], U)
