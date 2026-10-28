"""Addon annulus shape parity, candidate policies, symmetry and owned lifetime."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import skin_annuli
from anthroforge.native.mesh import NativeCancellation
from tools.check_skin_annuli import correspondence, evaluate

DATA = json.loads((Path(__file__).parent / "fixtures/skin/annuli.json").read_text())


@pytest.mark.parametrize("row", DATA["cases"])
def test_annulus_candidate_shape_matches_addon(session, row):
    surface, loops, result = evaluate(session.engine, row)
    snapshot = result.snapshot()
    actual = snapshot.samples[:, :3].reshape(5, -1, 3)
    error, _, _ = correspondence(actual, np.array(row["chosen"]["points"]))
    assert error < 3e-6
    assert snapshot.patches[0, 6] == ("direct", "planar", "radial").index(row["kind"])
    assert snapshot.patches[0, 8] == row["chosen"]["inversions"]
    expected_sources = row["chosen"]["sources"]
    assert [int(i) for i in snapshot.patches[0, 4:6] if i >= 0] == expected_sources
    np.testing.assert_array_equal(snapshot.quads, row["chosen"]["faces"])
    np.testing.assert_array_equal(surface.array(0), row["vertices"])
    assert len(loops.samples) == 2


def mirrored_guides(loops):
    positive = loops.samples.copy()
    positive[:, :, 0] += 1.5
    negative = positive.copy()
    negative[:, :, (0, 3)] *= -1
    negative[:, :, 1] += 0.001
    return replace(
        loops,
        samples=np.concatenate((positive, negative)),
        pairs=np.array([[0, 1], [2, 3]]),
        symmetric=np.zeros(4),
    )


def test_reflected_patches_reuse_source_geometry_without_changing_target_identity(session):
    surface, loops, _ = evaluate(session.engine, DATA["cases"][0])
    result = skin_annuli.build(surface, mirrored_guides(loops), [0, 0, 0, 1, 0, 0]).snapshot()
    first, second = result.patches
    assert first[7] == -1 and second[7] == 0
    np.testing.assert_array_equal(second[4:6], [2, 3])
    expected = result.samples[: second[0]].copy()
    expected[:, (0, 3)] *= -1
    np.testing.assert_array_equal(result.samples[second[0] :], expected)
    np.testing.assert_array_equal(
        result.quads[second[2] :], result.quads[: second[2], ::-1] + second[0]
    )


def test_annulus_lifetime_and_empty_inputs(session):
    surface, loops, result = evaluate(session.engine, DATA["cases"][0])
    snapshot = result.snapshot()
    result.close()
    result.close()
    assert len(snapshot.samples) == 300
    with pytest.raises(ValueError, match="Unknown skin annulus"):
        result.snapshot()
    empty = replace(loops, samples=np.empty((0, 192, 6)), pairs=np.empty((0, 2)), symmetric=[])
    assert skin_annuli.build(surface, empty).snapshot().patches.shape == (0, 9)


def test_annulus_rejects_invalid_pairs_bad_samples_and_cancellation(session):
    surface, loops, _ = evaluate(session.engine, DATA["cases"][0])
    with pytest.raises(ValueError, match="distinct valid"):
        skin_annuli.build(surface, replace(loops, pairs=[[0, 0]]))
    broken = loops.samples.copy()
    broken[0, 0, 0] = np.nan
    with pytest.raises(ValueError, match="Nonfinite"):
        skin_annuli.build(surface, replace(loops, samples=broken))
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_annuli.build(surface, loops, cancel=token.handle)
