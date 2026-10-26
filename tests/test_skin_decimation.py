"""Blender collapse policy, safe owned results and failure/cancellation boundaries."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import skin_proxy, topology
from anthroforge.native.mesh import NativeCancellation
from tools.check_skin_decimation import comparison, mesh

DATA = json.loads((Path(__file__).parent / "fixtures/skin/proxy_decimation.json").read_text())


@pytest.mark.parametrize("row", DATA["cases"], ids=lambda row: row["name"])
def test_proxy_preserves_blender_shape_and_source(session, row):
    source = mesh(session.engine, np.array(row["points"]), np.array(row["faces"]))
    result = skin_proxy.decimate(source, row["target"])
    assert result.counts[1] == row["target"]
    expected = np.array(row["result_points"]), np.array(row["result_faces"])
    actual = result.array(0), result.array(3)
    scale = np.linalg.norm(np.ptp(row["points"], axis=0))
    assert comparison(session.engine, actual, expected, scale)["maximum"] < row["tolerance"]
    np.testing.assert_array_equal(source.array(0), row["points"])
    np.testing.assert_array_equal(source.array(3), row["faces"])


def test_proxy_bypass_retains_full_precision(session):
    row = DATA["cases"][0]
    points = np.array(row["points"], dtype=float) + 0.123456789012345
    source = mesh(session.engine, points, np.array(row["faces"]))
    result = skin_proxy.decimate(source, len(row["faces"]))
    assert topology.same_content(source, result)


def test_proxy_rejects_invalid_settings_budget_and_cancel(session):
    row = DATA["cases"][0]
    source = mesh(session.engine, np.array(row["points"]), np.array(row["faces"]))
    with pytest.raises(ValueError, match="face target"):
        skin_proxy.decimate(source, 0)
    with pytest.raises(ValueError, match="memory budget"):
        skin_proxy.decimate(source, 32, budget=128)
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_proxy.decimate(source, 32, cancel=token.handle)


def test_proxy_tetrahedron_collapse_matches_blender_boundary_behavior(session):
    points = np.array([[1, 1, 1], [-1, -1, 1], [-1, 1, -1], [1, -1, -1]])
    faces = np.array([[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]])
    result = skin_proxy.decimate(mesh(session.engine, points, faces), 1)
    assert result.counts[1] == 2


def test_proxy_preserves_small_nonmanifold_input_as_blender_modifier_does(session):
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1]])
    faces = np.array([[0, 1, 2], [1, 0, 3], [0, 1, 4]])
    result = skin_proxy.decimate(mesh(session.engine, points, faces), 1)
    np.testing.assert_array_equal(result.array(0), points)
    np.testing.assert_array_equal(result.array(3), faces)
