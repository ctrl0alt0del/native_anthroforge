"""Same routing safety contract for both QP strategies, including bound and closed curves."""

import ctypes as c
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import numpy as np
import pytest

from anthroforge.native import path_collisions, routing
from anthroforge.native.mesh import NativeCancellation, pointer
from anthroforge.native.paths import Path
from tests.routing_backend_cases import all_cases, inputs

CASES = all_cases()


def quality(engine, path, spec, case):
    owners = case.get("contacts", spec.owners or (0,) * len(spec.curve.points))
    row = path_collisions.row(path, spec.world, owners)
    hits, _ = path_collisions.check(engine, [row], spec.handles, spec.matrices)
    points, parameters = path.array()[:, :3], path.array(1)
    pin_errors = [
        np.max(np.abs(points[parameters == i] - p.position))
        for i, p in enumerate(spec.curve.points)
    ]
    return dict(
        clear=bool(np.all(hits < 0)),
        finite=bool(np.isfinite(points).all()),
        monotonic=bool(np.all(np.diff(parameters) > 0)),
        pin_error=max(pin_errors),
    )


@pytest.mark.parametrize("backend", ["CUSTOM", "PIQP"])
@pytest.mark.parametrize("case", CASES, ids=lambda row: row["name"])
def test_route_backend_preserves_clearance_pins_and_warm_layout(session, backend, case):
    meshes, spec = inputs(session.engine, case)
    spec = replace(spec, backend=backend)
    path, report = routing.evaluate(session.engine, spec)
    for warm in (None, path):
        output, report = routing.evaluate(session.engine, replace(spec, warm=warm))
        check = quality(session.engine, output, spec, case)
        assert check["clear"] and check["finite"] and check["monotonic"], check
        assert check["pin_error"] < 1e-12
        assert report.backend == backend and report.counters[7]


def test_backends_are_per_invocation_on_concurrent_workers(session):
    case = next(row for row in CASES if row["name"] == "snapped_cube-128-fiber")
    meshes, spec = inputs(session.engine, case)
    choices = ("CUSTOM", "PIQP") * 4
    with ThreadPoolExecutor(max_workers=2) as executor:
        tasks = [
            executor.submit(routing.evaluate, session.engine, replace(spec, backend=b))
            for b in choices
        ]
        for backend, task in zip(choices, tasks, strict=True):
            path, report = task.result(timeout=10)
            assert report.backend == backend and quality(session.engine, path, spec, case)["clear"]


@pytest.mark.parametrize("backend", ["CUSTOM", "PIQP"])
def test_cancellation_and_unknown_backend_are_explicit(session, backend):
    meshes, spec = inputs(session.engine, CASES[0])
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancel"):
        routing.evaluate(session.engine, replace(spec, backend=backend), cancel.handle)
    with pytest.raises(ValueError, match="CUSTOM or PIQP"):
        routing.evaluate(session.engine, replace(spec, backend="OTHER"))


def legacy_route(engine, spec):
    options = routing.Options(
        spec.curve.engine_settings.samples, 24, spec.curve.closed, spec.curve.engine_settings.radius
    )
    counters, measures = np.zeros(8, dtype=np.int64), np.zeros(8)
    args = routing.arguments(routing.arrays(spec))
    handle = engine.library.af_route_path(
        *args, c.byref(options), counters.ctypes.data_as(routing.INT64), pointer(measures), 0, 0
    )
    return Path(engine, handle)


def test_original_abi_keeps_custom_default_without_extended_options(session):
    meshes, spec = inputs(session.engine, CASES[2])
    expected, _ = routing.evaluate(session.engine, spec)
    old = legacy_route(session.engine, spec)
    np.testing.assert_array_equal(old.array(), expected.array())
