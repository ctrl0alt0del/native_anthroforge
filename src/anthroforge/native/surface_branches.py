"""Owned native branch assembly inputs; geometry and correspondence stay in C++."""

import ctypes as c

from .curve_surfaces import INT, Row, Settings
from .mesh import GeometryEngine, Mesh, U


class Branch(c.Structure):
    _fields_ = [("boundary", c.c_int), ("count", c.c_int), ("rows", INT), ("roots", INT)]


def configure(engine: GeometryEngine) -> None:
    rows, branches = c.POINTER(Row), c.POINTER(Branch)
    engine.bind(
        "af_curve_surface_branches",
        [rows, c.c_int, c.c_int, branches, c.c_int, c.c_int, c.c_int, c.c_int, U],
        U,
    )


def branch(boundary: int, rows: list[int], roots: list[int]) -> Branch:
    if len(rows) != len(roots):
        raise ValueError("Every branch source needs an explicit main point.")
    values = Branch(
        boundary, len(rows), (c.c_int * len(rows))(*rows), (c.c_int * len(roots))(*roots)
    )
    return values


def geometry(
    engine: GeometryEngine,
    rows: list[Row],
    main: int,
    branches: list[Branch],
    settings: Settings,
    cancel: int = 0,
) -> Mesh:
    inputs = ((Row * len(rows))(*rows), len(rows), main)
    connections = ((Branch * len(branches))(*branches), len(branches))
    options = (settings.exact, settings.strips, settings.flip, cancel)
    handle = engine.library.af_curve_surface_branches(*inputs, *connections, *options)
    engine.check(not handle)
    return Mesh(engine, handle)
