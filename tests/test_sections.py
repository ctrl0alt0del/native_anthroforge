"""Cross-sections preserve source triangles and ignore clipped nearest hits."""

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.native import sections
from tests.conftest import CUBE


def test_cube_contour_and_original_triangle_picking(session):
    mesh = session.engine.import_mesh(CUBE, 1, False)
    report = sections.contours(mesh, IDENTITY, [0, 0, -1, 0])
    points = np.array(report["lines"])
    assert len(points) and np.max(np.abs(points[:, 2])) == 0
    hits = sections.pick(
        session.engine, [mesh.handle], [IDENTITY], [[0, 0, -1, 0]], [0, 0, 3], [0, 0, -1]
    )
    assert len(hits) == 1 and hits[0][7] == -0.5
    triangle = mesh.array(3)[int(hits[0][3])]
    np.testing.assert_allclose(np.array(hits[0][8:11]) @ mesh.array(0)[triangle], hits[0][5:8])


def test_coplanar_patch_emits_boundary_without_internal_diagonal(session):
    mesh = session.engine.create_mesh(
        [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], [0, 1, 2, 0, 2, 3], [0, 3, 6]
    )
    report = sections.contours(mesh, IDENTITY, [0, 0, 1, 0])
    assert report["coplanar_faces"] == 2 and len(report["lines"]) == 8
    lengths = np.linalg.norm(
        np.array(report["lines"])[::2] - np.array(report["lines"])[1::2], axis=1
    )
    np.testing.assert_allclose(lengths, 1)


def test_outside_plane_has_no_contours_or_visible_hit(session):
    mesh = session.engine.import_mesh(CUBE, 1, False)
    assert not sections.contours(mesh, IDENTITY, [1, 0, 0, -3])["lines"]
    assert not sections.pick(
        session.engine, [mesh.handle], [IDENTITY], [[1, 0, 0, -3]], [0, 0, 3], [0, 0, -1]
    )
    with pytest.raises(ValueError):
        sections.contours(mesh, IDENTITY, [0, 0, 0, 0])


def test_transformed_contours_use_world_plane(session):
    mesh = session.engine.import_mesh(CUBE, 1, False)
    frame = list(IDENTITY)
    frame[3], frame[7], frame[11] = 3, 2, 1
    report = sections.contours(mesh, frame, [0, 0, 1, -1])
    points = np.array(report["lines"])
    np.testing.assert_allclose(points[:, 2], 1)
    assert points[:, 0].min() == 2.5 and points[:, 1].min() == 1.5
