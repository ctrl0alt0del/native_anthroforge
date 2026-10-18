"""Pinned production-addon routing inputs; numerical parity is distinct from clearance."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.core.entities import IDENTITY
from anthroforge.native import routing

CASES = json.loads((Path(__file__).parent / "fixtures/routing/addon.json").read_text())["cases"]


def inputs(session, case):
    settings = RoutingSettings(samples=case["samples"], radius=case["radius"])
    source = Curve(
        tuple(CurvePoint(position=tuple(p)) for p in case["points"]),
        closed=case["closed"],
        engine_settings=settings,
    )
    meshes = collider_meshes(session, case)
    owners = tuple(1 if key else 0 for key in case["owners"])
    return meshes, routing.Inputs(
        source, tuple(m.handle for m in meshes), (IDENTITY,) * len(meshes), owners=owners
    )


def collider_meshes(session, case):
    return [
        session.engine.create_mesh(
            c["vertices"],
            np.asarray(c["triangles"]).reshape(-1),
            np.arange(len(c["triangles"]) + 1) * 3,
        )
        for c in case["colliders"]
    ]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["name"])
def test_production_routing_parity(session, case):
    meshes, spec = inputs(session, case)
    path, report = routing.evaluate(session.engine, spec)
    np.testing.assert_allclose(path.array()[:, :3], case["result"], atol=1e-10, rtol=0)
    assert report.counters[7] == (1 if case["closed"] else len(case["points"]) - 1)
