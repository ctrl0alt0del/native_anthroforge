"""Projection uses owned displayed geometry, world planes and native sampling."""

from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.native.strokes import Stroke, plane


def pointer(x=0, y=0, radius=1):
    return [x, y, 3, 0, 0, -1, x * 100, y * 100, radius]


def stroke(session, handles=(), frames=(), **options):
    settings = [
        options.get("surface", False),
        options.get("first", 0),
        options.get("offset", 0),
        options.get("relative", False),
    ]
    return Stroke(session.engine, handles, frames, [0, 0, 0, 0, 0, 1], settings)


def test_view_plane_probe_does_not_author_or_consume_points(session):
    value = stroke(session)
    assert value.probe(pointer(0.2, 0.4)) == pytest.approx([0.2, 0.4, 0, 1])
    assert value.count == 0 and not session.document.objects
    value.append(pointer(), False)
    value.append(pointer(0.12), True)
    np.testing.assert_allclose(value.read()[:, 0], [0, 0.03, 0.06, 0.09, 0.12])
    assert np.all(value.read()[:, 2] == 0)
    value.pop()
    assert value.count == 4


def mesh_stroke(session, assembly, **options):
    root, _ = assembly
    mesh = session.assets[session.document.entity(root).asset].mesh
    return stroke(session, [mesh.handle], [IDENTITY], surface=True, **options)


def test_surface_offset_and_miss_use_last_valid_depth(session, assembly):
    value = mesh_stroke(session, assembly, offset=0.1)
    assert value.probe(pointer())[2] == pytest.approx(0.6)
    value.append(pointer(), False)
    value.append(pointer(2), False)
    assert value.read()[-1, 2] == pytest.approx(0.6)


def test_first_hit_plane_and_radius_relative_offset(session, assembly):
    value = mesh_stroke(session, assembly, first=2, offset=0.1, relative=True)
    value.append(pointer(radius=2), False)
    value.append(pointer(2, radius=4), False)
    np.testing.assert_allclose(value.read()[:, 2], [0.7, 0.7])


def test_image_plane_preserves_affine_placement_and_parallel_rays_fail(session):
    frame = session.engine.transform([1, 2, 3, 0, 90, 0, 2, 3, 1])
    depth = plane(session.engine, frame)
    value = Stroke(session.engine, [], [], depth, [0, 0, 0, 0])
    ray = [3, 2, 3, -1, 0, 0, 0, 0, 1]
    assert value.probe(ray)[:3] == pytest.approx([1, 2, 3])
    with pytest.raises(ValueError, match="parallel"):
        value.probe(pointer())


def test_released_surface_keeps_stroke_snapshot_alive(session):
    mesh = session.engine.import_mesh(Path("examples/primitives/cube.obj"), 1, False)
    value = stroke(session, [mesh.handle], [IDENTITY], surface=True)
    del mesh
    assert value.probe(pointer())[2] == pytest.approx(0.5)


def test_view_change_preserves_samples_and_rebases_next_segment(session):
    value = stroke(session)
    value.append(pointer(), False)
    value.append(pointer(0.1), False)
    previous = value.read().copy()
    value.view([1, 0, 0])
    value.append([3, 0.2, 0.3, -1, 0, 0, 50, 40, 1])
    np.testing.assert_array_equal(value.read()[:2], previous)
    np.testing.assert_allclose(value.read()[-1], [0.1, 0.2, 0.3, 1])
    assert value.count == 3
