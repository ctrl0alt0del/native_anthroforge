"""Patch material locations must not move when only discretization changes."""

import numpy as np
import pytest

from anthroforge.core.tissue_settings import TissueInflation
from anthroforge.native import material_basis, material_bindings, tissue_shapes
from tests.test_adaptive_material_frames import all_records, frames, patch
from tests.test_material_bindings import IDENTITY


@pytest.mark.parametrize("resolution", [2, 4, 7])
def test_collinear_patch_resampling_preserves_positions_and_offset_frames(session, resolution):
    points = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
    before = patch(session.engine, points)
    after = patch(session.engine, [points[0], [0.4, 0, 0], *points[1:]], resolution)
    for source, target in ((before, after), (after, before)):
        rows = all_records(source)
        actual = material_bindings.frames(source, target, IDENTITY, rows)
        np.testing.assert_allclose(actual, frames(source, rows), atol=1e-9)


def corner_and_edge_records(mesh):
    original = all_records(mesh)
    result = []
    for weights in ([1, 0, 0], [0, 1, 0], [0, 0, 1], [0.5, 0.5, 0], [0, 0.5, 0.5]):
        rows = original.copy()
        rows[:, 3:6] = weights
        result.append(rows)
    return np.vstack(result)


@pytest.mark.parametrize("shell", [False, True])
def test_concave_patch_edges_and_corners_retain_offset_frames(session, shell):
    points = [[0, 0, 0], [2, 0, 0], [2, 1, 0], [1, 1, 0], [1, 2, 0], [0, 2, 0]]
    before = patch(session.engine, points)
    after = patch(session.engine, [points[0], [0.4, 0, 0], *points[1:]], 3)
    if shell:
        before, after = [
            tissue_shapes.normal(m, TissueInflation(amount=0.1, minimum=0.1))
            for m in (before, after)
        ]
    rows = corner_and_edge_records(before)
    result = material_bindings.frames(before, after, IDENTITY, rows)
    np.testing.assert_allclose(result, frames(before, rows), atol=2e-8)


def transformed_frames(before, rows, rotation, scale, shift):
    bare = rows.copy()
    bare[:, 15:18] = 0
    result = frames(before, rows).reshape(-1, 4, 4).copy()
    result[:, :3, :3] = rotation @ result[:, :3, :3]
    points = frames(before, bare).reshape(-1, 4, 4)[:, :3, 3]
    result[:, :3, 3] = scale * points @ rotation.T + shift
    result[:, :3, 3] += np.einsum("nij,nj->ni", result[:, :3, :3], rows[:, 15:18])
    return result.reshape(-1, 16)


def test_patch_resampling_with_rigid_motion_scale_and_owned_basis_roundtrip(session):
    points = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
    rotation = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    resampled = np.vstack([points[0], [0.4, 0, 0], points[1:]])
    before = patch(session.engine, points)
    after = patch(session.engine, 2 * resampled @ rotation.T + [3, 4, 5], 3)
    after = material_basis.restore(after, *material_basis.arrays(after))
    rows = corner_and_edge_records(before)
    result = material_bindings.frames(before, after, IDENTITY, rows)
    expected = transformed_frames(before, rows, rotation, 2, [3, 4, 5])
    np.testing.assert_allclose(result, expected, atol=2e-8)
