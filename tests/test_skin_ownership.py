"""Attribution retains geometric instances while sharing authored subtree budgets."""

from dataclasses import replace

import numpy as np
import pytest

from anthroforge.native import skin_ownership
from anthroforge.native.mesh import NativeCancellation
from anthroforge.native.skin_capture import Capture


def cloud(points):
    return Capture(
        np.array(points, dtype=float),
        np.empty((0, 3), dtype=np.int64),
        np.empty(0, dtype=np.int32),
        np.empty(0),
        np.empty((len(points), 3)),
    )


def query_mesh(engine, points):
    return engine.create_mesh(points, [0, 1, 2], [0, 3])


def test_mirrored_sources_cannot_overwrite_original_supports(session):
    points = [(-2, 0, 0), (2, 0, 0), (-1, 0, 0), (1, 0, 0), (-2, 0, 0.01), (2, 0, 0.01)]
    targets = [(-2, 0, 0.01), (2, 0, 0.01), (-2, 0, 0.02)]
    mesh = query_mesh(session.engine, targets)
    candidates = [[0], [1], [2], [3], [0, 2], [1, 3]]
    result = skin_ownership.evaluate(
        mesh, cloud(points), range(7), [0, 0, 1, 1, -1, -1], candidates
    )
    np.testing.assert_array_equal(result.owners, [0, 0, 0])
    np.testing.assert_array_equal(result.sources, [4, 5, 4])
    assert not result.fallback_count


def test_missing_support_uses_all_instances_and_reports_fallback(session):
    mesh = query_mesh(session.engine, [(-2, 0, 0.01), (2, 0, 0.01), (-1, 0, 0.02)])
    points = [(-2, 0, 0), (2, 0, 0), (-1, 0, 0)]
    result = skin_ownership.evaluate(mesh, cloud(points), range(4), [0, 0, 1], [[], [], []])
    np.testing.assert_array_equal(result.owners, [0, 0, 1])
    assert result.fallback_count == 3


def test_no_scp_retains_unowned_vertices_for_remainder_budget(session):
    mesh = query_mesh(session.engine, [[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    result = skin_ownership.evaluate(mesh, cloud([[0, 0, 0]]), [0, 1], [-1], [[]])
    assert result.fallback_count == 3
    np.testing.assert_array_equal(result.owners, -1)
    np.testing.assert_array_equal(skin_ownership.regions(session.engine, result.owners, [], 4), 4)


def test_centerline_midpoints_compete_as_zero_radius_samples(session):
    geo = cloud([[0, 0, 0], [2, 0, 0], [1, 0.1, 0]])
    geo = replace(
        geo,
        segments=np.array([[0, 1]], dtype=np.int64),
        segment_owners=np.array([0], dtype=np.int32),
    )
    mesh = query_mesh(session.engine, [[1, 0, 0], [1, 0, 0.01], [1.1, 0, 0]])
    result = skin_ownership.evaluate(mesh, geo, [0, 2, 3], [-1, 0], [[1], [1]])
    np.testing.assert_array_equal(result.sources, 0)
    np.testing.assert_array_equal(result.owners, 0)


def test_density_transfer_preserves_nearest_owner_and_length(session):
    source = query_mesh(session.engine, [[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    target = query_mesh(session.engine, [[0, 0.9, 0], [0.9, 0, 0], [0, 0, 0.1]])
    owners, lengths = skin_ownership.sample(source, target, [4, 5, 6], [0.1, 0.2, 0.3])
    np.testing.assert_array_equal(owners, [6, 5, 4])
    np.testing.assert_array_equal(lengths, [0.3, 0.2, 0.1])


def test_rejects_cross_source_indices_and_honors_cancellation(session):
    geo = cloud([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    geo = replace(
        geo, triangles=np.array([[0, 1, 2]], dtype=np.int64), owners=np.array([0], dtype=np.int32)
    )
    mesh = query_mesh(session.engine, geo.vertices)
    with pytest.raises(ValueError, match="crosses source"):
        skin_ownership.evaluate(mesh, geo, [0, 2, 3], [0, 1], [[0], [1]])
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_ownership.evaluate(mesh, geo, [0, 3], [0], [[0]], cancel=token.handle)


def test_small_island_cleanup_uses_neighbor_majority(session):
    points = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0.001, 0.001, 0]]
    mesh = session.engine.create_mesh(points, [0, 1, 2, 0, 3, 2, 0, 1, 3], [0, 3, 6, 9])
    result = skin_ownership.evaluate(
        mesh, cloud(points), range(5), [0, 0, 0, 1], [[0], [1], [2], [3]], ratio=0.001
    )
    np.testing.assert_array_equal(result.owners, [0, 0, 0, 0])
