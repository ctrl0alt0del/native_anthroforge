"""Owned native calls, independent acceptance checks, and observational measurements."""

import csv
import ctypes as c
import io
import time

import numpy as np

from anthroforge.native import path_collisions, routing
from anthroforge.native.mesh import GeometryEngine

from .cases import ROOT

LAB = ROOT / "build/routing-piqp/native/af_routing_lab.dll"
BACKENDS = ("current", "piqp-sparse", "piqp-dense")


def engine():
    result = GeometryEngine(LAB)
    result.bind("af_route_lab_configure", [c.c_int, c.c_int, c.c_int, c.c_double], None)
    result.bind("af_route_lab_records", [], c.c_char_p)
    return result


def configure(engine, backend, *, paired=False, audit=False, tolerance=1e-9):
    engine.library.af_route_lab_configure(backend, paired, audit, tolerance)


def records(engine):
    data = engine.library.af_route_lab_records().decode()
    return [
        {key: float(value) for key, value in row.items()}
        for row in csv.DictReader(io.StringIO(data))
    ]


def quality(engine, path, spec, case):
    owners = case.get("contacts", spec.owners or (0,) * len(spec.curve.points))
    row = path_collisions.row(path, spec.world, owners)
    hits, tolerance = path_collisions.check(engine, [row], spec.handles, spec.matrices)
    return dict(
        clear=bool(np.all(hits < 0)),
        collision_tolerance=tolerance,
        collision_segments=hits.tolist(),
        **path_quality(path, spec),
    )


def path_quality(path, spec):
    points, parameters = path.array()[:, :3], path.array(1)
    pin_errors = [
        float(np.max(np.abs(points[parameters == i] - p.position)))
        for i, p in enumerate(spec.curve.points)
    ]
    edges = np.diff(np.vstack((points, points[:1])) if path.closed else points, axis=0)
    result = dict(
        pin_error=max(pin_errors),
        monotonic=bool(np.all(np.diff(parameters) > 0)),
        finite=bool(np.isfinite(points).all()),
        length=float(np.linalg.norm(edges, axis=1).sum()),
        samples=path.count,
    )
    return dict(result, points=points.tolist(), parameters=parameters.tolist())


def measure(engine, spec):
    begin, cpu = time.perf_counter_ns(), time.process_time_ns()
    try:
        path, report = routing.evaluate(engine, spec)
        result = dict(ok=True, counters=report.counters, measures=report.measures)
    except ValueError as error:
        path, result = None, dict(ok=False, error=str(error))
    result.update(
        wall_ms=(time.perf_counter_ns() - begin) / 1e6, cpu_ms=(time.process_time_ns() - cpu) / 1e6
    )
    return path, result
