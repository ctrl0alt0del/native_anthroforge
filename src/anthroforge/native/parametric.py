"""Compile once, sample XYZ and curve frames in one owned native call."""

import ctypes as c
from typing import Any

import numpy as np

from anthroforge.core.expressions import Symbol
from anthroforge.core.parametric import ParametricSettings

from . import expressions
from .construction import curve_records
from .mesh import INT64, D, GeometryEngine, U, pointer
from .paths import Path


def configure(engine: GeometryEngine) -> None:
    inputs = [c.POINTER(U), c.c_int, INT64, D, D, c.c_int]
    domain = [c.c_int, c.c_int, c.c_double, c.c_double]
    engine.bind("af_parametric_interpolated_path", [*inputs, *domain, c.c_int, c.c_int, D, U], U)


def evaluate(engine: GeometryEngine, curve: Any, cancel: int = 0) -> tuple[Path, Any]:
    settings = curve.engine_settings
    symbols = (
        Symbol("t"),
        *(Symbol(v.name, v.numeric_type, v.dimension) for v in settings.variables),
    )
    values = {"t": 0.0, **{v.name: v.value for v in settings.variables}}
    programs = tuple(
        equation(engine, getattr(settings, axis), symbols, axis.upper(), cancel) for axis in "xyz"
    )
    start, end = interval(engine, settings, cancel)
    return sample(engine, curve, programs, values, (start, end), cancel)


def equation(engine: GeometryEngine, source: str, symbols: Any, label: str, cancel: int) -> Any:
    try:
        return expressions.compile(engine, source, symbols, cancel)
    except ValueError as error:
        raise ValueError(f"Parametric {label} expression '{source}': {error}") from error


def interval(
    engine: GeometryEngine, settings: ParametricSettings, cancel: int
) -> tuple[float, float]:
    symbols = tuple(Symbol(v.name, v.numeric_type, v.dimension) for v in settings.variables)
    values = {v.name: v.value for v in settings.variables}
    return tuple(
        endpoint(engine, settings.interval, name, symbols, values, cancel)
        for name in ("start", "end")
    )  # type: ignore[return-value]


def endpoint(
    engine: GeometryEngine, interval: Any, name: str, symbols: Any, values: Any, cancel: int
) -> float:
    expression = getattr(interval, name + "_expression")
    if not expression:
        return float(getattr(interval, name))
    program = equation(engine, expression, symbols, "interval " + name, cancel)
    program.output.require("REAL", "SCALAR")
    return float(program.evaluate(values, cancel))


def sample(
    engine: GeometryEngine, curve: Any, programs: Any, values: Any, interval: Any, cancel: int
) -> tuple[Path, Any]:
    handles = (U * 3)(*(p.handle for p in programs))
    integers, reals = expressions.frames(programs[0].symbols, [values])
    metadata = curve_records(curve)
    count = curve.engine_settings.resolution
    output = np.empty((count, 13))
    inputs = (handles, len(programs[0].symbols), integers.ctypes.data_as(INT64), pointer(reals))
    domain = (pointer(metadata), len(curve.points), count, curve.path_closed, *interval)
    interpolation = interpolation_options(curve.engine_settings)
    handle = engine.library.af_parametric_interpolated_path(
        *inputs, *domain, *interpolation, pointer(output), cancel
    )
    return Path(engine, handle), output


def interpolation_options(config: ParametricSettings) -> tuple[int, int]:
    return int(config.interpolation == "POLYLINE"), config.bezier_resolution
