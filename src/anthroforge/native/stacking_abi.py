"""Owned batched numerical stacking ABI; no execution threads are created here."""

import ctypes as c
from typing import Any

from .mesh import INT64, D, U


class Material(c.Structure):
    _fields_ = [(name, D) for name in ("vertices", "weights", "constraint_weights")]
    _fields_ += [(name, INT64) for name in ("faces", "interpolation", "fixed", "constraints")]
    _fields_ += [
        (name, c.c_int)
        for name in (
            "vertices_count",
            "faces_count",
            "samples",
            "width",
            "fixed_count",
            "constraint_count",
        )
    ]


class Domain(c.Structure):
    _fields_ = [("id", U)] + [(name, D) for name in ("base", "own", "direction")]
    _fields_ += [(name, INT64) for name in ("faces", "parts", "sources")]
    _fields_ += [
        (name, c.c_int) for name in ("vertices", "triangles", "family", "root", "enabled", "side")
    ]
    _fields_ += [("allowance", c.c_double), ("material", Material)]


class Settings(c.Structure):
    _fields_ = [
        (name, c.c_double)
        for name in (
            "search",
            "area",
            "epsilon",
            "clearance",
            "radius",
            "strength",
            "blend",
            "preservation",
            "adjustment",
        )
    ]
    _fields_ += [("cache_bytes", U), ("result_bytes", U), ("fragment_limit", c.c_int)]


class Policy(c.Structure):
    _fields_ = [(name, U) for name in ("first", "second", "cover")]
    _fields_ += [(name, c.c_int) for name in ("excluded", "invalid", "offset", "count", "mode")]


class Obstacle(c.Structure):
    _fields_ = [("vertices", D), ("faces", INT64), ("count", c.c_int), ("triangles", c.c_int)]


class Accepted(c.Structure):
    _fields_ = [("id", U), ("points", D), ("count", c.c_int), ("status", c.c_int)]


class Output(c.Structure):
    _fields_ = [("id", U), ("status", c.c_int), ("vertices", c.c_int64)]
    _fields_ += [(name, c.c_double) for name in ("maximum", "map_ms", "solve_ms", "validation_ms")]
    _fields_ += [
        (name, c.c_int64) for name in ("baseline_self", "baseline_bone_crossings", "open_obstacles")
    ]
    _fields_ += [("baseline_penetration", c.c_double), ("message", c.c_char * 256)]


class Order(c.Structure):
    _fields_ = [(name, U) for name in ("first", "second", "underlying", "covering")]
    _fields_ += [("status", c.c_int), ("warnings", c.c_int)]
    _fields_ += [(name, c.c_double * 2) for name in ("positive", "negative")]
    _fields_ += [(name, c.c_double) for name in ("coincident", "minimum", "maximum")]
    _fields_ += [(name, c.c_int64) for name in ("fragments", "points", "crossings")]
    _fields_ += [("diagnostic", c.c_char * 128)]


def configure(engine: Any) -> None:
    engine.bind("af_stack_create", [], U)
    engine.bind("af_stack_release", [U], None)
    engine.bind("af_stack_sizes", [U, INT64])
    engine.bind("af_stack_results", [U, c.POINTER(Output), c.c_int])
    engine.bind("af_stack_orders", [U, c.POINTER(Order), c.c_int])
    engine.bind("af_stack_dependencies", [U, c.POINTER(U), c.c_int])
    engine.bind("af_stack_points", [U, U, D, c.c_int, D])
    engine.bind("af_stack_run", RUN_ARGUMENTS)
    engine.bind("af_stack_plan", RUN_ARGUMENTS)
    engine.bind("af_stack_resolve", [U, c.POINTER(Accepted), c.c_int, c.POINTER(U), c.c_int, U])


RUN_ARGUMENTS = [
    U,
    c.POINTER(Domain),
    c.c_int,
    c.POINTER(Settings),
    c.POINTER(Policy),
    c.c_int,
    INT64,
    c.c_int,
    c.POINTER(Obstacle),
    c.c_int,
    U,
]
