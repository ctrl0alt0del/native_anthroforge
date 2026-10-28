"""FLOW sampling preserves the addon interior stencils and accepted material identity."""

import json

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.native import skin_guides, tissue_inflation
from tests.test_tissue_inflation import FIXTURE, grid_mesh, settings


def fixture(engine):
    case = json.loads(FIXTURE.read_text())["cases"][0]
    base = grid_mesh(engine, case["points"])
    current = tissue_inflation.evaluate(base, settings(case["settings"]), False)
    return base, current, np.array(case["points"]).shape


def expected(grid):
    along, across = np.gradient(grid, axis=1), np.gradient(grid, axis=0)
    normal = np.cross(across, along)
    position, direction, normals = [v[1:-1:2, 1:-1:3].reshape(-1, 3) for v in (grid, along, normal)]
    lengths, areas = np.linalg.norm(direction, axis=1), np.linalg.norm(normals, axis=1)
    valid = (lengths > 1e-12) & (areas > 1e-12)
    return np.column_stack(
        (
            position[valid],
            direction[valid] / lengths[valid, None],
            normals[valid] / areas[valid, None],
            np.zeros(valid.sum()),
        )
    )


def test_chart_sampling_matches_addon_stencil(session):
    base, current, shape = fixture(session.engine)
    output = skin_guides.charts(base, current, IDENTITY, False)
    grid = current.array(0).reshape(shape)
    np.testing.assert_allclose(output.samples, expected(grid), atol=1e-12)
    np.testing.assert_allclose(output.points, grid[len(grid) // 2, ::3], atol=1e-12)
    np.testing.assert_array_equal(output.offsets, [0, len(output.points)])


def test_reflection_transforms_normal_without_changing_source(session):
    base, current, _ = fixture(session.engine)
    frame = list(IDENTITY)
    frame[0] = -1
    first = skin_guides.charts(base, current, IDENTITY, False)
    second = skin_guides.charts(base, current, frame, False)
    expected_samples = first.samples.copy()
    expected_samples[:, [0, 3, 6]] *= -1
    np.testing.assert_allclose(second.samples, expected_samples, atol=1e-12)


def test_chart_frame_rejects_invalid_buffers(session):
    base, current, _ = fixture(session.engine)
    with pytest.raises(ValueError, match="sixteen"):
        skin_guides.charts(base, current, [1], False)


def test_two_row_branch_preserves_addon_missing_interior_rejection(session):
    from anthroforge.native import tissue_parts
    from tests.test_tissue_branches import CASES, inputs

    base, parts = inputs(session, CASES[0])
    current = tissue_parts.evaluate(base, parts, "a", False)
    # The captured addon branch has only two rows: its interior stencil is empty.
    with pytest.raises(ValueError, match="no nondegenerate interior"):
        skin_guides.charts(base, current, IDENTITY, False)
