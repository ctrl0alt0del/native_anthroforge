"""Evaluated original skull geometry and endpoint routes, distinct from saved baked paths."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.core.entities import IDENTITY
from anthroforge.native import routing
from tests.test_routing_parity import collider_meshes

FIXTURE = json.loads((Path(__file__).parent / "fixtures/routing/skull.json").read_text())


def inputs(session, case):
    meshes = collider_meshes(session, FIXTURE)
    settings = RoutingSettings(samples=case["samples"], radius=case["radius"])
    curve = Curve(
        tuple(CurvePoint(position=tuple(p)) for p in case["points"]), engine_settings=settings
    )
    return meshes, routing.Inputs(
        curve,
        tuple(m.handle for m in meshes),
        (IDENTITY,) * len(meshes),
        owners=tuple(case["owners"]),
    )


@pytest.mark.parametrize("case", FIXTURE["cases"], ids=lambda row: row["name"])
def test_skull_cold_and_warm_routes_match_addon(session, case):
    meshes, value = inputs(session, case)
    cold, cold_report = routing.evaluate(session.engine, value)
    warm, warm_report = routing.evaluate(session.engine, replace(value, warm=cold))
    np.testing.assert_allclose(cold.array()[:, :3], case["result"], atol=1e-10, rtol=0)
    np.testing.assert_allclose(warm.array()[:, :3], case["warm"], atol=1e-10, rtol=0)
    assert cold_report.counters[7] == warm_report.counters[7] == 1
