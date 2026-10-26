"""Shared symmetry preserves source shape and winding without adding cut caps."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import skin_symmetry
from anthroforge.native.mesh import NativeCancellation
from anthroforge.native.skin_guides import Guides
from tools.check_skin_symmetry import compare, evaluate

DATA = json.loads((Path(__file__).parent / "fixtures/skin/symmetry.json").read_text())
PLANE = [0, 0, 0, 1, 0, 0]


@pytest.mark.parametrize("row", DATA["cases"])
def test_symmetry_matches_addon_non_degenerate_surface_and_winding(session, row):
    source, result = evaluate(session.engine, row)
    report = compare(result, row)
    assert report["error"] < 3e-7 and report["connectivity"]
    assert report["degenerate_source_faces"] == (12 if row["name"] == "on-vertices" else 0)
    np.testing.assert_array_equal(source.array(0), row["vertices"])


def test_flow_half_keeps_all_samples_and_only_contiguous_negative_path_runs(session):
    points = np.array(
        [[-1, 0, 0], [-1, 1, 0], [0, 2, 0], [-1, 3, 0], [-1, 4, 0], [1, 5, 0], [-1, 6, 0]]
    )
    source = Guides(np.array([[1, 2, 3, 0, 1, 0, 0, 0, 1, 0]]), points, np.array([0, 7]), [[3, 0]])
    result = skin_symmetry.guides(session.engine, source, PLANE)
    np.testing.assert_array_equal(result.points, points[[0, 1, 3, 4]])
    np.testing.assert_array_equal(result.offsets, [0, 2, 4])
    np.testing.assert_array_equal(result.samples, source.samples)
    np.testing.assert_array_equal(result.regions, source.regions)


def test_symmetry_rejects_invalid_planes_empty_half_and_cancelled_work(session):
    source, _ = evaluate(session.engine, DATA["cases"][0])
    with pytest.raises(ValueError, match="plane"):
        skin_symmetry.half(source, [0, 0, 0, 0, 0, 0])
    with pytest.raises(ValueError, match="no source surface"):
        skin_symmetry.half(source, [-2, 0, 0, 1, 0, 0])
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_symmetry.half(source, PLANE, token.handle)
