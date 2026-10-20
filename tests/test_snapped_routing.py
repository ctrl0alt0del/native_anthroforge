"""Exact user pins and donor bound-box: validate segments, not only sampled vertices."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.native import path_collisions, paths, routing
from tests.test_routing_parity import CASES, inputs

CASE = json.loads((Path(__file__).parent / "fixtures/routing/snapped_cube.json").read_text())


def fixture_inputs(session, bound, samples):
    surface = CASE["surfaces"][0]
    triangles = np.asarray(surface["triangles"])
    mesh = session.engine.create_mesh(
        surface["vertices"], triangles.ravel(), np.arange(len(triangles) + 1) * 3
    )
    curve = Curve(
        tuple(CurvePoint(position=tuple(p)) for p in CASE["points"]),
        engine_settings=RoutingSettings(samples=samples),
    )
    return mesh, routing.Inputs(
        curve, (mesh.handle,), (tuple(surface["matrix"]),), owners=(1, 1) if bound else ()
    )


def collisions(session, path, value):
    row = path_collisions.row(path, value.world, (1,) * len(value.curve.points))
    result, _ = path_collisions.check(session.engine, [row], value.handles, value.matrices)
    return result


def require_clear(session, path, value):
    assert np.all(collisions(session, path, value) < 0)
    for index, point in enumerate(value.curve.points):
        np.testing.assert_allclose(
            path.array()[path.array(1) == index, :3], [point.position], atol=1e-12, rtol=0
        )


@pytest.mark.parametrize("bound", [False, True])
@pytest.mark.parametrize("samples", [32, 64, 128])
def test_snapped_cube_cold_and_warm_paths_have_clear_segments(session, bound, samples):
    mesh, value = fixture_inputs(session, bound, samples)
    cold, _ = routing.evaluate(session.engine, value)
    require_clear(session, cold, value)
    warm, _ = routing.evaluate(session.engine, replace(value, warm=cold))
    require_clear(session, warm, value)


def donor_path(session, case):
    positions = np.asarray(case["result"])
    samples = np.zeros((len(positions), 11))
    samples[:, :3], samples[:, 5], samples[:, 7], samples[:, 9] = positions, 1, 1, 1
    return paths.restore(session.engine, samples, np.linspace(0, 1, len(samples)), False)


def test_bound_box_intentionally_corrects_donor_pin_penetration(session):
    case = next(case for case in CASES if case["name"] == "bound-box")
    meshes, value = inputs(session, case)
    original = donor_path(session, case)
    assert np.any(collisions(session, original, value) >= 0)
    corrected, _ = routing.evaluate(session.engine, value)
    require_clear(session, corrected, value)
