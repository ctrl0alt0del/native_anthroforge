"""Batched native surface sampling, explicit alignment and owned mesh results."""

import ctypes as c
from dataclasses import dataclass
from typing import Any

import numpy as np

from .mesh import D, GeometryEngine, Mesh, U, doubles, pointer
from .paths import Path

INT = c.POINTER(c.c_int)


class Row(c.Structure):
    _fields_ = [
        ("path", U),
        ("matrix", c.c_double * 16),
        ("start", c.c_double),
        ("span", c.c_double),
        ("origin", c.c_double),
        ("reverse", c.c_int),
        ("samples", c.c_int),
        ("alignment_reverse", c.c_int),
        ("station_count", c.c_int),
        ("station_parameters", D),
        ("station_values", D),
    ]


@dataclass(frozen=True)
class Settings:
    exact: bool = True
    strips: int = 0
    patch: bool = False
    patch_resolution: int = 4
    close_across: bool = False
    flip: bool = False


def configure(engine: GeometryEngine) -> None:
    from . import surface_branches

    rows = c.POINTER(Row)
    engine.bind("af_curve_surface_layout", [rows, c.c_int, c.c_int, c.c_int, D, INT, U])
    engine.bind(
        "af_curve_surface_geometry",
        [rows, c.c_int, c.c_int, INT, c.c_int, c.c_int, c.c_int, c.c_int, U],
        U,
    )
    surface_branches.configure(engine)
    configure_symmetry(engine)


def configure_symmetry(engine: GeometryEngine) -> None:
    engine.bind(
        "af_curve_surface_mirror_order", [c.POINTER(Row), c.c_int, D, c.c_int, c.c_double, INT, U]
    )


def mirror_order(
    engine: GeometryEngine, rows: list[Row], world: Any, rule: Any, cancel: int
) -> Any:
    output = np.empty(2 * len(rows), dtype=np.int32)
    frame = doubles(world)
    inputs = (Row * len(rows))(*rows), len(rows), pointer(frame)
    plane = ("X", "Y", "Z").index(rule.axis), rule.shift
    count = engine.library.af_curve_surface_mirror_order(
        *inputs,
        *plane,
        output.ctypes.data_as(INT),
        cancel,
    )
    engine.check(count < 0)
    return tuple(map(int, output[:count]))


def row(path: Path, frame: Any, use: Any, origin: float = -1, reverse: bool = False) -> Row:
    if len(frame) != 16:
        raise ValueError("Surface input needs a full affine frame.")
    result = Row(
        path.handle,
        (c.c_double * 16)(*frame),
        use.start or 0,
        1 if use.span is None else use.span,
        origin,
        use.reverse,
        32 if use.samples is None else use.samples,
        reverse,
    )
    result._path_owner = path
    return result


def correspondence(row: Row, values: Any) -> Row:
    if not values:
        return row
    parameters = np.ascontiguousarray([p for p, _ in values], dtype=np.float64)
    stations = np.ascontiguousarray([s for _, s in values], dtype=np.float64)
    row.station_count = len(values)
    row.station_parameters, row.station_values = pointer(parameters), pointer(stations)
    row._station_owner = (parameters, stations)
    return row


def layout(
    engine: GeometryEngine, rows: list[Row], settings: Settings, cancel: int = 0
) -> tuple[Any, Any]:
    alignment = np.empty((len(rows), 2))
    across = np.empty(max(0, len(rows) - 1), dtype=np.int32)
    inputs = ((Row * len(rows))(*rows), len(rows), settings.exact, settings.strips)
    engine.check(
        engine.library.af_curve_surface_layout(
            *inputs, pointer(alignment), across.ctypes.data_as(INT), cancel
        )
    )
    return alignment, across


def geometry(
    engine: GeometryEngine, rows: list[Row], across: Any, settings: Settings, cancel: int = 0
) -> Mesh:
    counts = np.ascontiguousarray(across, dtype=np.int32)
    if counts.shape != (max(0, len(rows) - 1),):
        raise ValueError("Surface layout needs one density per adjacent source pair.")
    inputs = ((Row * len(rows))(*rows), len(rows), settings.exact, counts.ctypes.data_as(INT))
    options = (settings.patch, settings.patch_resolution, settings.close_across, settings.flip)
    handle = engine.library.af_curve_surface_geometry(*inputs, *options, cancel)
    engine.check(not handle)
    return Mesh(engine, handle)
