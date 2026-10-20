"""Projection uses owned displayed geometry, world planes and native sampling."""

from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.native.mesh import NativeCancellation
from anthroforge.native.strokes import Stroke, plane


def assert_outward_depth(actual, expected):
    # Projection adds a sub-micrometre outward margin at this fixture scale.
    delta = actual - np.asarray(expected)
    assert np.all(delta >= 0) and np.max(delta) < 1e-6


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


def test_temporary_snap_chooses_nearest_surface_and_restores_view_plane(session):
    meshes = [island(session, 0, z) for z in (0.5, 1.5)]
    value = stroke(session, [m.handle for m in meshes], [IDENTITY] * 2)
    value.append(pointer(), False)
    value.snapping(True)
    assert value.probe(pointer())[2] == pytest.approx(1.5)
    assert value.count == 1
    value.append(pointer(), False)
    value.snapping(False)
    assert value.probe(pointer())[2] == 0
    value.append(pointer(0.2), False)
    assert_outward_depth(value.read()[:, 2], [0, 1.5, 0])
    value.pop()
    assert value.probe(pointer())[2] == 0


def test_temporary_snap_miss_uses_configured_plane_and_does_not_lock_it(session):
    mesh = island(session, 0, 1.5)
    value = stroke(session, [mesh.handle], [IDENTITY], surface=True, first=2)
    value.append(pointer(0.2), False)
    value.snapping(True)
    assert value.probe(pointer())[2] == pytest.approx(1.5)
    assert value.probe(pointer(0.2))[2] == 0
    value.append(pointer(), False)
    value.snapping(False)
    assert value.probe(pointer())[2] == 0


def test_temporary_snap_respects_world_transforms_and_relative_offset(session):
    mesh = island(session, 0, 0)
    frame = session.engine.transform([0, 0, 1, 0, 0, 0, 1, 2, 3])
    value = stroke(session, [mesh.handle], [frame], offset=0.1, relative=True)
    value.snapping(True)
    assert value.probe(pointer(radius=2))[2] == pytest.approx(1.2)
    value.append(pointer(radius=2), False)
    value.pop()
    assert value.count == 0 and value.probe(pointer(radius=3))[2] == pytest.approx(1.3)


def mesh_stroke(session, assembly, **options):
    root, _ = assembly
    mesh = session.assets[session.document.entity(root).asset].mesh
    return stroke(session, [mesh.handle], [IDENTITY], surface=True, **options)


def island(session, x, z):
    vertices = [[x + dx, y, z] for dx, y in ((-0.01, -1), (0.01, -1), (0.01, 1), (-0.01, 1))]
    return session.engine.create_mesh(vertices, [0, 1, 2, 3], [0, 4])


def test_blender_projects_target_before_depth_substeps(session):
    meshes = [island(session, x, z) for x, z in ((0, 0.5), (0.12, 1.5))]
    value = stroke(session, [m.handle for m in meshes], [IDENTITY] * 2, surface=True)
    value.append(pointer(0), False)
    value.append(pointer(0.12), True)
    assert_outward_depth(value.read()[:, 2], [0.5, 1.5, 1.5, 1.5, 1.5])


def test_missed_target_keeps_precomputed_depth_but_next_event_uses_substep_hit(session):
    meshes = [island(session, x, z) for x, z in ((0, 0.5), (0.12, 1.5))]
    value = stroke(session, [m.handle for m in meshes], [IDENTITY] * 2, surface=True)
    value.append(pointer(-0.06), False)
    value.append(pointer(0.18), True)
    assert value.read()[-1, 2] == pytest.approx(0)
    value.append(pointer(0.2), False)
    assert value.read()[-1, 2] == pytest.approx(1.5)


@pytest.mark.parametrize("first", [1, 2, 3])
def test_first_event_plane_locks_even_when_initial_ray_misses_surface(session, first):
    mesh = island(session, 0.12, 1.5)
    value = stroke(session, [mesh.handle], [IDENTITY], surface=True, first=first)
    value.append(pointer(0), False)
    value.append(pointer(0.12), False)
    np.testing.assert_allclose(value.read()[:, 2], [0, 0])


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
    assert_outward_depth(value.read()[:, 2], [0.7, 0.7])


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


def test_batch_matches_pointer_projection_without_authoring(session, assembly):
    rays = [pointer(0.1), pointer(0.3), pointer(0.8)]
    value = mesh_stroke(session, assembly, offset=0.05)
    for ray in rays:
        value.append(ray)
    before = session.document
    result = session.command(
        "drawing.project",
        rays=rays,
        surfaces=[assembly[0]],
        plane=[0, 0, 0, 0, 0, 1],
        settings=dict(depth="SURFACE", offset=0.05),
    )
    np.testing.assert_allclose(result, value.read())
    assert session.document is before


def test_failed_batch_rolls_back_partial_projection_and_can_continue(session):
    value = stroke(session)
    value.append(pointer())
    bad = pointer(0.2)
    bad[3:6] = [1, 0, 0]
    with pytest.raises(ValueError, match="parallel"):
        value.batch([pointer(0.1), bad], False)
    assert value.count == 1 and len(value.read()) == 1
    value.append(pointer(0.3), False)
    assert value.count == 2


def test_batch_cancellation_preserves_existing_stroke(session):
    value = stroke(session)
    value.append(pointer())
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancel"):
        value.batch([pointer(0.1)], cancel=cancel.handle)
    assert value.count == 1


def test_tangent_view_plane_preserves_surface_tangent_during_camera_change(session):
    mesh = session.engine.create_mesh([[-2, -2, -2], [2, -2, 2], [0, 2, 0]], [0, 1, 2], [0, 3])
    value = stroke(session, [mesh.handle], [IDENTITY], surface=True, first=3)
    value.append(pointer(), False)
    # View normal projected into the z=x surface: the locked plane has z=-x.
    assert value.probe(pointer(0.2))[:3] == pytest.approx([0.2, 0, -0.2])
    value.view([1, 0, 0])
    assert value.probe(pointer(0.3))[:3] == pytest.approx([0.3, 0, -0.3])


def test_profiler_attributes_owned_preview_capacity(session):
    from anthroforge.profiling.construction_inventory import stroke_inventory

    value = stroke(session)
    empty = value.bytes
    value.batch([pointer(0), pointer(0.3)])
    report = stroke_inventory(dict(preview={value}))
    assert report["unique_bytes"] == value.bytes > empty
    assert report["unattributed_bytes"] == 0


@pytest.mark.parametrize("pixels,count", [(1, 1), (1.1, 2), (4, 2), (5.9, 3), (8, 3), (9, 4)])
def test_blender_distance_filter_and_depth_substep_rounding(session, pixels, count):
    value = stroke(session)
    value.append(pointer())
    value.append(pointer(pixels / 100))
    assert value.count == count


def test_sampled_plane_stroke_filters_motion_without_depth_substeps(session):
    value = stroke(session)
    value.append(pointer(), False, sample=True)
    value.append(pointer(0.009), False, sample=True)
    value.append(pointer(0.5), False, sample=True)
    assert value.count == 2
    value.append(pointer(0.5), False)
    assert value.count == 3  # Explicit placement does not apply the motion filter.


def test_pixel_tolerance_and_closure_are_native_and_nonmutating(session):
    value = stroke(session)
    value.batch([pointer(0), pointer(1), pointer(1, 1), pointer(0.08)], False)
    before = value.read().copy()
    assert value.settings() == pytest.approx(dict(error=0.08, closed=True))
    assert not value.settings(close_radius=7.9)["closed"]
    np.testing.assert_array_equal(value.read(), before)
    value.pop()
    assert not value.settings()["closed"]
    value.append(pointer(0), False)
    assert value.settings()["closed"]


def test_view_change_prevents_closure_using_unrelated_screen_coordinates(session):
    value = stroke(session)
    value.batch([pointer(0), pointer(1), pointer(1, 1)], False)
    value.view([1, 0, 0])
    value.append([3, 0, 0, -1, 0, 0, 0, 0, 1], False)
    assert not value.settings()["closed"]
