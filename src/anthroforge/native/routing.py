"""Batched production routing; all preparation, iteration and geometry queries are native."""

import ctypes as c
from dataclasses import dataclass
from typing import Any

import numpy as np

from anthroforge.core.construction import Curve
from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.core.entities import IDENTITY

from .construction import curve_records
from .mesh import INT64, D, GeometryEngine, U, doubles, pointer
from .paths import Path
from .point_attachments import INT
from .routing_scene import capture


class Options(c.Structure):
    _fields_ = [(name, c.c_int) for name in ("samples", "accepted_steps", "closed")]
    _fields_ += [("radius", c.c_double)]
    _fields_ += [("backend", c.c_int)]


@dataclass(frozen=True)
class Inputs:
    curve: Curve
    handles: tuple[int, ...] = ()
    matrices: tuple[tuple[float, ...], ...] = ()
    world: tuple[float, ...] = IDENTITY
    owners: tuple[int, ...] = ()
    warm: Path | None = None
    backend: str = "CUSTOM"


@dataclass(frozen=True)
class Report:
    counters: tuple[int, ...]
    measures: tuple[float, ...]
    backend: str = "CUSTOM"


def configure(engine: GeometryEngine) -> None:
    engine.bind(
        "af_route_path",
        [D, c.c_int, D, INT, c.POINTER(U), D, c.c_int, c.POINTER(Options), INT64, D, U, U],
        U,
    )
    engine.bind(
        "af_route_path_in_scene", [D, c.c_int, D, INT, U, c.POINTER(Options), INT64, D, U, U], U
    )


def arrays(inputs: Inputs) -> tuple[Any, ...]:
    count = len(inputs.curve.points)
    owners = np.asarray(inputs.owners or (0,) * count, dtype=np.int32)
    handles = np.asarray(inputs.handles, dtype=np.uint64)
    matrices, world = doubles(inputs.matrices), doubles(inputs.world)
    if owners.shape != (count,) or matrices.size != len(handles) * 16 or world.size != 16:
        raise ValueError("Routing requires one owner per knot and one transform per surface.")
    return curve_records(inputs.curve), owners, handles, matrices, world


def evaluate(engine: GeometryEngine, inputs: Inputs, cancel: int = 0) -> tuple[Path, Report]:
    settings = inputs.curve.engine_settings
    if not isinstance(settings, RoutingSettings):
        raise ValueError("Routing requires the routed curve engine.")
    if inputs.backend not in ("CUSTOM", "PIQP"):
        raise ValueError("ROUTED solver must be CUSTOM or PIQP.")
    options = Options(
        settings.samples,
        settings.accepted_steps,
        inputs.curve.closed,
        settings.radius,
        int(inputs.backend == "PIQP"),
    )
    return invoke(engine, arrays(inputs), options, inputs.warm, cancel)


def invoke(
    engine: GeometryEngine,
    packed: tuple[Any, ...],
    options: Options,
    warm: Path | None,
    cancel: int,
) -> tuple[Path, Report]:
    scene = capture(engine, packed, options.radius, cancel)
    counters, measures = np.zeros(8, dtype=np.int64), np.zeros(8)
    report_args = (c.byref(options), counters.ctypes.data_as(INT64), pointer(measures))
    handle = engine.library.af_route_path_in_scene(
        *arguments(packed)[:4], scene.handle, *report_args, warm.handle if warm else 0, cancel
    )
    return Path(engine, handle), read_report(counters, measures, options)


def read_report(counters: Any, measures: Any, options: Options) -> Report:
    return Report(
        tuple(counters.tolist()), tuple(measures.tolist()), "PIQP" if options.backend else "CUSTOM"
    )


def arguments(packed: tuple[Any, ...]) -> tuple[Any, ...]:
    data, owners, handles, matrices, world = packed
    surfaces = (handles.ctypes.data_as(c.POINTER(U)), pointer(matrices), len(handles))
    return pointer(data), len(data), pointer(world), owners.ctypes.data_as(INT), *surfaces
