"""Conforming quad splits preserve parent labels and never modify accepted input geometry."""

import numpy as np
import pytest

from anthroforge.native import skin_ownership, skin_proximity, skin_topology
from anthroforge.native.mesh import NativeCancellation
from tests.test_skin_ownership import cloud


def grid(engine, columns=3, rows=2):
    points = [[x, y, 0.03 * x * y] for y in range(rows + 1) for x in range(columns + 1)]
    faces = []
    for y in range(rows):
        for x in range(columns):
            a = y * (columns + 1) + x
            faces.append([a, a + 1, a + columns + 2, a + columns + 1])
    return engine.create_mesh(points, np.array(faces).ravel(), np.arange(len(faces) + 1) * 4)


def test_refinement_closes_neighbor_splits_and_retains_parent_labels(session):
    mesh = grid(session.engine, 2, 1)
    before = mesh.array(0).copy()
    result = skin_topology.split(mesh, [1, 0], [2, 0], [7, -1])
    assert result.mesh.counts[:2] == (12, 6)
    np.testing.assert_array_equal(result.regions, [2, 2, 2, 2, 0, 0])
    np.testing.assert_array_equal(result.guides, [7, 7, 7, 7, -1, -1])
    np.testing.assert_array_equal(mesh.array(0), before)
    faces = result.mesh.array(1).reshape(-1, 4)
    assert all(len(set(face)) == 4 for face in faces)


def test_adaptive_refinement_approaches_target_and_skips_guide_faces(session):
    mesh = grid(session.engine)
    values = np.full(mesh.counts[0], 0.3)
    result = skin_topology.refine(mesh, mesh, values, 24)
    assert result.mesh.counts[1] == 24
    skipped = skin_topology.refine(mesh, mesh, values, 24, regions=np.full(6, 2))
    assert skipped.mesh.counts[1] == 6
    np.testing.assert_array_equal(skipped.mesh.array(0), mesh.array(0))


def test_native_density_target_uses_area_and_largest_edge(session):
    mesh = grid(session.engine)
    assert skin_proximity.base_target(mesh, np.full(mesh.counts[0], 1.0), 8100) == 1000
    assert skin_proximity.base_target(mesh, np.full(mesh.counts[0], 0.01), 8100) == 8100


def test_proximity_matches_smoothstep_and_density_multiplier(session):
    mesh = grid(session.engine)
    geo = cloud(mesh.array(0))
    data = skin_ownership.pack(geo, [0, mesh.counts[0]], [-1], [[]])
    original = np.full(mesh.counts[0], 0.2)
    result = skin_proximity.evaluate(mesh, data, [1], original)
    np.testing.assert_array_equal(result.weights, 1.0)
    np.testing.assert_allclose(result.lengths, 0.2 / np.sqrt(1.5))
    assert result.statistics[0] == result.statistics[1] == mesh.counts[0]
    np.testing.assert_array_equal(original, 0.2)


def test_missing_proximity_sources_bypass_adjustment(session):
    mesh = grid(session.engine)
    data = skin_ownership.pack(cloud([[0, 0, 0]]), [0, 1], [-1], [[]])
    result = skin_proximity.evaluate(mesh, data, [0], np.ones(mesh.counts[0]))
    np.testing.assert_array_equal(result.lengths, 1.0)
    np.testing.assert_array_equal(result.weights, 0.0)
    assert result.statistics[0] == 0


def test_refinement_rejects_triangles_invalid_planes_and_cancel(session):
    mesh = grid(session.engine)
    triangle = session.engine.create_mesh([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [0, 1, 2], [0, 3])
    with pytest.raises(ValueError, match="requires quads"):
        skin_topology.split(triangle, [1])
    with pytest.raises(ValueError, match="symmetry plane"):
        skin_topology.refine(mesh, mesh, np.ones(mesh.counts[0]) * 0.1, 24, plane=[0] * 6)
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_topology.split(mesh, np.ones(6), cancel=token.handle)
