"""Warm continuation remaps each authored span instead of moving isolated sample indices."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import routing
from tests.test_routing_parity import inputs

CASES = json.loads((Path(__file__).parent / "fixtures/routing/warm.json").read_text())["cases"]


@pytest.mark.parametrize("case", CASES, ids=lambda row: row["name"])
def test_warm_continuation_matches_addon_remapping(session, case):
    meshes, spec = inputs(session, case["original"])
    warm, _ = routing.evaluate(session.engine, spec)
    points = tuple(
        replace(point, position=tuple(position))
        for point, position in zip(spec.curve.points, case["points"], strict=True)
    )
    settings = replace(spec.curve.engine_settings, samples=case["samples"])
    changed = replace(spec, curve=replace(spec.curve, points=points, engine_settings=settings))
    path, report = routing.evaluate(session.engine, replace(changed, warm=warm))
    np.testing.assert_allclose(path.array()[:, :3], case["result"], atol=1e-10, rtol=0)
    assert report.counters[7] == (1 if case["original"]["closed"] else len(points) - 1)
