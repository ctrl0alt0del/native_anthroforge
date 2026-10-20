"""Actual four-pin failure: retain feasible corridor bends through solver preparation."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import decode
from anthroforge.native import path_collisions, paths, routing

CASE = json.loads((Path(__file__).parent / "fixtures/routing/solver_fail1.json").read_text())
CONTACTS = (1, 1, 2, 2)


def colliders(session):
    return [
        session.engine.create_mesh(
            s["vertices"], np.array(s["triangles"]).ravel(), np.arange(len(s["triangles"]) + 1) * 3
        )
        for s in CASE["surfaces"]
    ]


def inputs(session, samples=24, bound=False, closed=False):
    meshes = colliders(session)
    settings = decode("ROUTED", dict(CASE["settings"], samples=samples))
    curve = Curve(
        tuple(CurvePoint(position=tuple(p)) for p in CASE["points"]),
        engine_settings=settings,
        closed=closed,
    )
    return meshes, routing.Inputs(
        curve,
        tuple(m.handle for m in meshes),
        tuple(tuple(s["matrix"]) for s in CASE["surfaces"]),
        tuple(CASE["matrix"]),
        CONTACTS if bound else (),
    )


def collisions(session, path, value):
    row = path_collisions.row(path, value.world, CONTACTS)
    result, _ = path_collisions.check(session.engine, [row], value.handles, value.matrices)
    return result


def require_clear(session, path, value):
    assert (collisions(session, path, value) < 0).all()
    parameters, samples = path.array(1), path.array()
    assert np.all(np.diff(parameters) > 0) and np.isfinite(samples).all()
    for i, point in enumerate(value.curve.points):
        np.testing.assert_allclose(
            samples[parameters == i, :3], [point.position], atol=1e-12, rtol=0
        )


@pytest.mark.parametrize("bound", [False, True])
@pytest.mark.parametrize("samples", [3, 4, 16, 24, 64])
def test_actual_cold_and_warm_route_keeps_pins_and_clear_segments(session, samples, bound):
    meshes, value = inputs(session, samples, bound)
    cold, report = routing.evaluate(session.engine, value)
    require_clear(session, cold, value)
    assert cold.count >= samples and report.counters[7] == 3
    assert cold.count > samples if samples < 16 else cold.count == samples
    warm, _ = routing.evaluate(session.engine, replace(value, warm=cold))
    require_clear(session, warm, value)
    assert value.curve.engine_settings.samples == samples


def test_closed_route_preserves_loop_correspondence_with_automatic_growth(session):
    meshes, value = inputs(session, 4, closed=True)
    path, report = routing.evaluate(session.engine, value)
    require_clear(session, path, value)
    assert path.closed and path.count > 4 and path.array(1)[-1] < 4
    assert not np.array_equal(path.array()[0, :3], path.array()[-1, :3])
    assert report.counters[7] == 1
    warm, _ = routing.evaluate(session.engine, replace(value, warm=path))
    require_clear(session, warm, value)


def test_rejected_baseline_seed_still_fails_whole_segment_validation(session):
    meshes, value = inputs(session)
    groups = CASE["rejected_seed"]
    vertices = np.concatenate([np.asarray(g)[int(i > 0) :] for i, g in enumerate(groups)])
    parameters = np.concatenate(
        [np.linspace(i, i + 1, len(g))[int(i > 0) :] for i, g in enumerate(groups)]
    )
    samples = np.zeros((len(vertices), 11))
    samples[:, :3], samples[:, 5], samples[:, 7], samples[:, 9] = vertices, 1, 1, 1
    path = paths.restore(session.engine, samples, parameters, False)
    np.testing.assert_array_equal(collisions(session, path, value), [[3, 20]])
