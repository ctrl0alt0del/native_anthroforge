"""Precise component picking through overlapping anatomy with cached native AABBs."""

import numpy as np

from anthroforge.native.components import PickIndex


def test_curve_picking_hits_between_samples_and_deduplicates_curve_labels(session):
    lines = [[-1, 0, 0], [0, 0, 0], [0, 0, 0], [1, 0, 0], [-1, 0, -1], [1, 0, -1]]
    index = PickIndex(session.engine, lines, True, [0, 0, 1])
    assert index.pick([0.25, 0, 2], [0, 0, -1], 0.01) == 0
    assert index.pick([0, 0, 2], [0, 0, -1], 0.01, 1) == 1
    assert index.pick([0.25, 0.1, 2], [0, 0, -1], 0.01) == -1


def test_cached_points_keep_owned_coordinates_and_handle_depth(session):
    points = np.array([[0, 0, 0], [0, 0, -1]], dtype=float)
    index = PickIndex(session.engine, points)
    points[:] = 100
    assert index.pick([0, 0, 1], [0, 0, -1], 0.01) == 0
    assert index.pick([0, 0, 1], [0, 0, -1], 0.01, 1) == 1
    assert index.pick([0, 0, 1], [0, 0, 1], 0.01) == -1


def test_segment_endpoints_and_parallel_rays(session):
    index = PickIndex(session.engine, [[0, 0, 0], [1, 0, 0]], True)
    assert index.pick([0.5, 0.001, 0], [1, 0, 0], 0.01) == 0
    assert index.pick([1.005, 0, 1], [0, 0, -1], 0.01) == 0
    assert index.pick([1.02, 0, 1], [0, 0, -1], 0.01) == -1
