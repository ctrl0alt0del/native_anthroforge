"""Optional bounded production-route evidence, copied on the worker into portable records."""

import ctypes as c
from typing import Any

import numpy as np

from anthroforge.core.curve_engines import RoutingSettings

from . import routing
from .mesh import INT64, D, U, pointer
from .routing_scene import capture

STAGES = ("Reference", "Planner", "Solver seed", "Solver trial", "Final")
TERMINATIONS = {0: "Running", 1: "Converged", 2: "Stalled", 3: "Iteration limit", 4: "Unsafe"}


def configure(engine: Any) -> None:
    engine.bind(
        "af_route_inspect",
        [D, c.c_int, D, c.POINTER(c.c_int), U, c.POINTER(routing.Options), U, U, c.c_int],
        U,
    )
    engine.bind("af_route_trace_info", [U, INT64, INT64, D])
    engine.bind("af_route_trace_records", [U], INT64)
    engine.bind("af_route_trace_buffer", [U, c.c_int], D)
    engine.bind("af_route_trace_error", [U], c.c_char_p)
    engine.bind("af_route_trace_release", [U], None)


def inspect(engine: Any, inputs: routing.Inputs, cancel: int = 0) -> dict[str, Any]:
    handle = invoke(engine, inputs, cancel)
    engine.check(not handle)
    try:
        return read(engine, handle, inputs.backend)
    finally:
        engine.library.af_route_trace_release(handle)


def invoke(engine: Any, inputs: routing.Inputs, cancel: int) -> int:
    settings, packed = inputs.curve.engine_settings, routing.arrays(inputs)
    if not isinstance(settings, RoutingSettings) or inputs.backend not in ("CUSTOM", "PIQP"):
        raise ValueError("Route inspection requires ROUTED and a supported backend.")
    options = routing.Options(
        settings.samples, settings.accepted_steps, inputs.curve.closed, settings.radius
    )
    scene = capture(engine, packed, settings.radius, cancel)
    args = (*routing.arguments(packed)[:4], scene.handle, c.byref(options))
    return int(
        engine.library.af_route_inspect(
            *args, inputs.warm.handle if inputs.warm else 0, cancel, int(inputs.backend == "PIQP")
        )
    )


def read(engine: Any, handle: int, backend: str) -> dict[str, Any]:
    lib = engine.library
    info, counters, measures = np.zeros(7, dtype=np.int64), np.zeros(8, dtype=np.int64), np.zeros(8)
    engine.check(
        lib.af_route_trace_info(
            handle, info.ctypes.data_as(INT64), counters.ctypes.data_as(INT64), pointer(measures)
        )
    )
    return decoded(lib, handle, info, counters, measures, backend)


def decoded(
    lib: Any, handle: int, info: Any, counters: Any, measures: Any, backend: str
) -> dict[str, Any]:
    result = metadata(info, backend)
    result.update(
        counters=counters.tolist(),
        measures=measures.tolist(),
        error=lib.af_route_trace_error(handle).decode("utf-8", errors="replace"),
        records=records(lib, handle, info),
    )
    return result


def metadata(info: Any, backend: str) -> dict[str, Any]:
    return dict(
        backend=backend,
        success=bool(info[4]),
        warm=bool(info[5]),
        attempts=int(info[6]),
        omitted=int(info[3]),
        limits=dict(records=128, points=131072, contacts=4096),
    )


def records(lib: Any, handle: int, info: Any) -> list[dict[str, Any]]:
    rows = buffer(lib.af_route_trace_records(handle), int(info[0]), 10)
    points = buffer(lib.af_route_trace_buffer(handle, 0), int(info[1]), 3)
    contacts = buffer(lib.af_route_trace_buffer(handle, 1), int(info[2]), 17)
    return [record(row, points, contacts) for row in rows]


def buffer(data: Any, count: int, width: int) -> Any:
    return np.ctypeslib.as_array(data, shape=(count, width)) if count else np.empty((0, width))


def record(row: Any, points: Any, contacts: Any) -> dict[str, Any]:
    stage, span, attempt, trial, accepted, termination, begin, count, first, length = map(int, row)
    return dict(
        stage=STAGES[stage],
        span=span,
        attempt=attempt,
        trial=trial,
        accepted=accepted,
        termination=TERMINATIONS.get(termination, str(termination)),
        points=points[begin : begin + count].tolist(),
        contacts=contacts[first : first + length].tolist(),
    )
