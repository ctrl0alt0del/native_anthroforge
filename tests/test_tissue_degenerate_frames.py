"""Collapsed material poles must not turn round-off into inflation directions."""

import numpy as np
import pytest

from anthroforge.core.tissue_settings import SectionProfile, TissueInflation
from anthroforge.native import material, tissue_inflation, topology
from tests.test_tissue_inflation import grid_mesh


def pole_grid():
    u = np.linspace(0, 1, 19)
    v = np.linspace(0, 1, 7)
    return np.array([[(x, y * x, 0) for x in u] for y in v])


def generated_grid(session, grid):
    regular = grid.copy()
    regular[:, :, 1] = np.linspace(0, 1, len(grid))[:, None]
    base = grid_mesh(session.engine, regular)
    arrays = [base.array(i) for i in range(5)]
    arrays[0] = grid.reshape(-1, 3)
    return material.restore(topology.restore(session.engine, arrays), material.array(base))


@pytest.mark.parametrize("direction", ["LOCAL", "SMOOTH", "SECTION"])
def test_profile_ignores_roundoff_normals_at_collapsed_boundary(session, direction):
    grid = pole_grid()
    settings = TissueInflation(mode="SECTION_PROFILE", profile=SectionProfile(direction=direction))
    original = tissue_inflation.evaluate(generated_grid(session, grid), settings)
    grid[0, 0] += (0, 1e-14, 1e-14)
    changed = tissue_inflation.evaluate(generated_grid(session, grid), settings)
    np.testing.assert_allclose(changed.array(0), original.array(0), atol=1e-11, rtol=0)
    np.testing.assert_array_equal(changed.array(0).reshape(grid.shape)[:, 0], grid[:, 0])
