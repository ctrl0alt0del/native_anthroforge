"""Density preserves exclusive budgets while smoothing transitions in logarithmic space."""

import numpy as np
import pytest

from anthroforge.native import skin_density, skin_proximity
from anthroforge.native.mesh import NativeCancellation
from tests.conftest import CUBE


def fixture(session):
    mesh = session.engine.import_mesh(CUBE, 1, False)
    return mesh, np.array([0, 0, 0, 0, 1, 1, 1, 1])


def test_density_conserves_regional_quad_estimates(session):
    mesh, regions = fixture(session)
    result = skin_density.evaluate(mesh, regions, [16, 64])
    for i, target in enumerate((16, 64)):
        mask = regions == i
        assert np.sum(result.areas[mask] / result.lengths[mask] ** 2) == pytest.approx(target)
    assert result.areas.sum() == pytest.approx(6)
    np.testing.assert_array_equal(result.unusable, [0, 0])


def test_empty_and_zero_budget_regions_are_explicit(session):
    mesh, regions = fixture(session)
    result = skin_density.evaluate(mesh, regions, [0, 0, 100], iterations=0)
    np.testing.assert_array_equal(result.unusable, [1, 1, 1])
    np.testing.assert_array_equal(result.lengths, np.ones(8))
    np.testing.assert_array_equal(result.region_areas[2:], [0])


def test_refinement_input_is_copied_and_corrected(session):
    mesh, regions = fixture(session)
    values = np.linspace(0.1, 0.5, 8)
    original = values.copy()
    result = skin_density.evaluate(mesh, regions, [16, 64], initial=values)
    np.testing.assert_array_equal(values, original)
    assert not np.array_equal(result.lengths, original)


def test_density_rejects_invalid_regions_and_cancels(session):
    mesh, regions = fixture(session)
    with pytest.raises(ValueError, match="region"):
        skin_density.evaluate(mesh, regions, [16])
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_density.evaluate(mesh, regions, [16, 64], cancel=token.handle)


def test_adaptive_base_reserves_guides_and_respects_full_target(session):
    mesh, _ = fixture(session)
    assert skin_proximity.base_target(mesh, np.full(8, 0.05), 8100, 300) == 2700
    assert skin_proximity.base_target(mesh, np.full(8, 0.001), 8100, 300) == 8100
    assert skin_proximity.base_target(mesh, np.ones(8), 8100, 0) == 1000
    with pytest.raises(ValueError, match="length"):
        skin_proximity.base_target(mesh, np.full(8, -1), 8100, 0)
