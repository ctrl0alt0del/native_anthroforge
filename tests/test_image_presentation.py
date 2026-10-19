"""Image visibility and landmarks agree with native plane geometry under affine transforms."""

import numpy as np
import pytest

from anthroforge.application import curve_sources, storage
from anthroforge.core.entities import IDENTITY
from anthroforge.core.image_presentation import settings
from anthroforge.native import images
from tests.test_reference_images import loaded, source


def test_native_image_pick_has_top_left_uv_and_world_distance(session):
    result = images.pick(session.engine, [IDENTITY], [[2, 1]], [0], [-0.5, 0.25, 3], [0, 0, -2])
    assert result[0].tolist() == pytest.approx([0, 3, 0.25, 0.25, -0.5, 0.25, 0, 1])
    assert not len(images.pick(session.engine, [IDENTITY], [[2, 1]], [2], [0, 0, 3], [0, 0, -1]))
    assert not len(images.pick(session.engine, [IDENTITY], [[2, 1]], [0], [2, 0, 3], [0, 0, -1]))


def test_affine_plane_pick_and_calibration_use_same_coordinate_convention(session):
    frame = (2.0, 1.0, 0.0, 3.0, 0.0, 3.0, 0.0, -2.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0)
    hit = images.pick(session.engine, [frame], [[2, 2]], [1], [2.5, -0.5, 4], [0, 0, -1])[0]
    assert hit[2:4].tolist() == pytest.approx([0.25, 0.25])
    size = images.calibrate(session.engine, frame, [2, 2], [0, 0, 1, 1], np.sqrt(40))
    assert size == pytest.approx([2, 2])


def test_image_appearance_is_per_workspace_and_does_not_recompute(session, tmp_path):
    target = loaded(session, source(tmp_path))
    before, cursor = session.document.object(target), session.history.cursor
    jobs = [j.id for j in session.scheduler.jobs if j.writes]
    session.command("image.presentation", target=target, depth="FRONT", opacity=0.3, pickable=False)
    assert session.document.object(target) == before and session.history.cursor == cursor
    assert jobs == [j.id for j in session.scheduler.jobs if j.writes]
    assert settings(session.workspace, target).depth == "FRONT"
    path = tmp_path / "image.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    restored, _ = storage.read_package(path, session.engine)
    assert restored.workspaces == session.document.workspaces


def test_reference_image_reparenting_preserves_world_placement(session, tmp_path):
    target = loaded(session, source(tmp_path), values=[1, 2, 3, 10, 20, 30, 1, 1, 1])
    parent = session.command("curve.create")
    session.command("object.transform", target=parent, values=[2, 0, 1, 10, 20, 30, 2, 3, 4])
    frame = curve_sources.world(session.engine, session.document, target)
    session.command("object.reparent", target=target, parent=parent)
    assert curve_sources.world(session.engine, session.document, target) == pytest.approx(frame)
    session.command("object.reparent", target=target)
    assert session.document.object(target).matrix == pytest.approx(frame)


def test_image_axis_alignment_retains_position_and_scale(session, tmp_path):
    target = loaded(session, source(tmp_path), values=[1, 2, 3, 0, 0, 0, 2, 3, 4])
    session.command("image.align", target=target, axis="X")
    values = session.engine.decompose(session.document.object(target).matrix)
    assert values[:3] == pytest.approx([1, 2, 3])
    assert values[6:] == pytest.approx([2, 3, 4])
    frame = np.array(session.document.object(target).matrix).reshape(4, 4)
    assert frame[:3, 2] == pytest.approx([4, 0, 0])


def test_native_image_pick_rejects_bad_inputs(session):
    with pytest.raises(ValueError, match="same images"):
        images.pick(session.engine, [IDENTITY], [], [0], [0, 0, 0], [0, 0, 1])
    with pytest.raises(ValueError, match="positive dimensions"):
        images.pick(session.engine, [IDENTITY], [[0, 1]], [0], [0, 0, 0], [0, 0, 1])
    with pytest.raises(ValueError, match="Invalid image picking ray"):
        images.pick(session.engine, [IDENTITY], [[1, 1]], [0], [0, 0, 0], [0, 0, 0])


def test_native_axis_visibility_uses_blender_local_z_tolerance(session):
    frames = [
        session.engine.transform([0, 0, 0, angle, 0, 0, 2, 3, -4]) for angle in (0, 0.1, 0.2, 90)
    ]
    assert images.aligned(session.engine, frames, [0, 0, -2]).tolist() == [1, 1, 0, 0]
    shear = list(IDENTITY)
    shear[2] = 1
    assert images.aligned(session.engine, [shear], [1, 0, 1]).tolist() == [1]
    assert images.aligned(session.engine, [shear], [0, 0, 1]).tolist() == [0]
    with pytest.raises(ValueError, match="view axis"):
        images.aligned(session.engine, frames, [0, 0, 0])


def test_axis_visibility_is_presentation_only_and_persists(session, tmp_path):
    target = loaded(session, source(tmp_path))
    original, cursor = session.document.object(target), session.history.cursor
    session.command("image.presentation", target=target, only_axis_aligned=True)
    assert session.document.object(target) == original and session.history.cursor == cursor
    path = tmp_path / "aligned.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    restored, _ = storage.read_package(path, session.engine)
    assert settings(restored.workspaces[0], target).only_axis_aligned


def test_reflected_image_side_matches_transformed_winding(session):
    frame = session.engine.transform([0, 0, 0, 0, 0, 0, -1, 1, 1])
    front = images.pick(session.engine, [frame], [[2, 1]], [1], [0, 0, 3], [0, 0, -1])
    back = images.pick(session.engine, [frame], [[2, 1]], [2], [0, 0, 3], [0, 0, -1])
    assert len(front) == 0 and len(back) == 1
