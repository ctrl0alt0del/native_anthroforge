"""A folded provider uses its far normal intersection, retaining ordinary solver contracts."""

from copy import deepcopy

import numpy as np
import pytest

from anthroforge.native.stacking import StackSession
from tests.stacking_fixtures import domain, settings
from tests.test_tissue_stacking_native import CASES


def folded_provider():
    case = deepcopy(CASES[0])
    under, cover = case["domains"]
    for index, point in enumerate(under["own"]):
        point[0], point[2] = [-2, 2, -2][index % 3], [0.2, 0.4, 0.6][index % 3]
    for point in cover["base"]:
        point[0], point[1], point[2] = point[0] / 2, point[1] / 2, 0.05
    cover["own"] = (np.array(cover["base"]) + [0, 0, 0.1]).tolist()
    cover["material"]["vertices"] = deepcopy(cover["base"])
    under["material"]["fixed"], cover["material"]["fixed"] = [], []
    return case


def solve(session, case, native=None):
    native = native or StackSession(session.engine)
    packed = [domain(row) for row in case["domains"]]
    output, _ = native.run([p[0] for p in packed], settings(case["settings"]))
    row = output[case["domains"][1]["id"]]
    assert row["status"] == 1, row["message"]
    return native, row


@pytest.mark.parametrize("direction", [[0, 0, 1], [0.6, 0, 0.8]])
def test_ambiguous_support_uses_geometry_normal_not_inflation_direction(session, direction):
    case = folded_provider()
    cover = case["domains"][1]
    cover["direction"] = [direction] * len(cover["base"])
    _, result = solve(session, case)
    points = result["points"]
    expected = 0.5 - points[:, 0] * 0.05 + 0.1
    np.testing.assert_allclose(points[:, 2], expected, atol=0.003)
    np.testing.assert_allclose(points[:, :2], np.array(cover["own"])[:, :2], atol=1e-7)
    assert result["metrics"][2] == len(points)
    assert result["metrics"][8] < 2e-7 and result["metrics"][9] < 2e-7


def test_changed_fold_recomputes_support_then_reuses_result(session):
    case = folded_provider()
    native, before = solve(session, case)
    for point in case["domains"][0]["own"]:
        point[2] += 0.1
    _, changed = solve(session, case, native)
    assert np.min(changed["points"][:, 2] - before["points"][:, 2]) > 0.09
    _, reused = solve(session, case, native)
    np.testing.assert_array_equal(reused["points"], changed["points"])
    assert reused["metrics"][23] == 1
