"""Pinned addon Fiber surface construction, separate from presentation tubes."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.native import paths, skin_capture

CASES = json.loads((Path(__file__).parent / "fixtures/skin/fiber_bevel.json").read_text())["cases"]


def path_from_points(engine, points, closed=False):
    samples = np.zeros((len(points), 11))
    samples[:, :3] = points
    samples[:, 5] = samples[:, 6] = samples[:, 9] = 1
    return paths.restore(engine, samples, np.linspace(0, 1, len(points)), closed)


@pytest.mark.parametrize("row", CASES, ids=lambda row: row["name"])
def test_addon_bevel_vertices_and_connectivity(session, row):
    path = path_from_points(session.engine, row["points"], row.get("closed", False))
    mesh = skin_capture.fiber_bevel(path, IDENTITY, row["radius"])
    np.testing.assert_allclose(mesh.array(0), row["output"]["vertices"], atol=1e-8, rtol=0)
    np.testing.assert_array_equal(mesh.array(1), np.array(row["output"]["faces"]).ravel())
    np.testing.assert_array_equal(mesh.array(3), row["output"]["triangles"])


@pytest.mark.parametrize("radius", [0, -1, float("nan"), float("inf")])
def test_bevel_rejects_invalid_radius(session, radius):
    path = path_from_points(session.engine, [[0, 0, 0], [0, 0, 1]])
    with pytest.raises(ValueError, match="positive radius"):
        skin_capture.fiber_bevel(path, IDENTITY, radius)
