"""Native closed guides match addon projection, closure, pairing and deduplication."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import skin_loops
from anthroforge.native.mesh import NativeCancellation
from tools.check_skin_loops import curve as path
from tools.check_skin_loops import evaluate as prepare
from tools.check_skin_loops import normal_ambiguities

DATA = json.loads((Path(__file__).parent / "fixtures/skin/loops.json").read_text())


@pytest.mark.parametrize("row", DATA["cases"])
def test_loop_preparation_matches_addon_and_preserves_sources(session, row):
    surface, curves, result = prepare(session.engine, row)
    np.testing.assert_array_equal(result.sources, row["sources"])
    np.testing.assert_array_equal(result.sources[result.pairs], row["pairs"])
    np.testing.assert_allclose(result.samples[:, :, :3], row["points"], atol=3e-6, rtol=0)
    normal_ambiguities(session.engine, row, result)
    np.testing.assert_array_equal(result.symmetric, row["symmetric"])
    assert [i for i, state in enumerate(result.statuses) if state == 1] == row["unpaired"]
    for curve, points in zip(curves, row["paths"], strict=True):
        np.testing.assert_array_equal(curve.array()[:, :3], points)
    np.testing.assert_array_equal(surface.array(0), row["vertices"])


def test_loop_preparation_reports_duplicate_and_unpaired_inputs(session):
    _, _, result = prepare(session.engine, DATA["cases"][0])
    np.testing.assert_array_equal(result.statuses, [0, 0, 2, 1])


def test_loop_preparation_rejects_open_paths_bad_planes_and_cancellation(session):
    surface, curves, _ = prepare(session.engine, DATA["cases"][0])
    opened = path(session.engine, curves[0].array()[:, :3], closed=False)
    with pytest.raises(ValueError, match="closed path"):
        skin_loops.prepare(surface, [opened], [np.eye(4)])
    with pytest.raises(ValueError, match="symmetry plane"):
        skin_loops.prepare(surface, curves, [np.eye(4)] * 4, [0] * 6)
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_loops.prepare(surface, curves, [np.eye(4)] * 4, cancel=token.handle)


def test_empty_loop_capture_is_valid(session):
    surface, _, _ = prepare(session.engine, DATA["cases"][0])
    result = skin_loops.prepare(surface, [], [])
    assert result.samples.shape == (0, 192, 6)
    assert not len(result.pairs) and not len(result.statuses)


def test_reflected_loop_capture_uses_world_frames(session):
    surface, curves, before = prepare(session.engine, DATA["cases"][0])
    reflection = np.diag([-1.0, 1, 1, 1])
    result = skin_loops.prepare(surface, curves, [reflection] * len(curves))
    expected = before.samples[:, :, :3].copy()
    expected[:, :, 0] *= -1
    np.testing.assert_allclose(result.samples[:, :, :3], expected, atol=1e-12)
    np.testing.assert_array_equal(result.pairs, before.pairs)


def test_collapsed_loop_is_reported_without_fabricating_a_patch(session):
    surface, _, _ = prepare(session.engine, DATA["cases"][0])
    collapsed = path(session.engine, [[0, 0, 1], [0, 0, 2], [0, 0, 3]])
    result = skin_loops.prepare(surface, [collapsed], [np.eye(4)])
    np.testing.assert_array_equal(result.statuses, [3])
    assert not len(result.samples) and not len(result.pairs)
