"""Native contracts needed by view-relative transforms and signed surface offsets."""

from types import SimpleNamespace

import numpy as np
import pytest

from anthroforge.desktop import authoring_actions, authoring_state
from anthroforge.desktop.curve_interaction import offset_hit
from anthroforge.native import scene


def test_view_axis_rotation_is_world_space_and_preserves_its_axis(session):
    axis = np.array([1, 2, 3], dtype=float)
    angles = scene.axis_rotation(session.engine, axis, 73)
    matrix = session.engine.transform([0, 0, 0, *angles, 1, 1, 1])
    assert session.engine.world_point(matrix, axis) == pytest.approx(axis)
    rotation = np.array(matrix).reshape(4, 4)[:3, :3]
    assert rotation.T @ rotation == pytest.approx(np.eye(3))
    assert np.trace(rotation) == pytest.approx(1 + 2 * np.cos(np.radians(73)))


@pytest.mark.parametrize("axis,angle", [([0, 0, 0], 2), ([0, 1, 0], float("nan"))])
def test_invalid_view_rotation_fails(session, axis, angle):
    with pytest.raises(ValueError):
        scene.axis_rotation(session.engine, axis, angle)


@pytest.mark.parametrize("scale", [(2, 3, 4), (-2, 3, 4), (-2, -3, -4)])
def test_surface_normal_transforms_as_covector(session, scale):
    mesh = session.engine.create_mesh([[0, 0, 0], [1, 0, 1], [0, 1, 0]], [0, 1, 2], [0, 3])
    matrix = session.engine.transform([2, 1, 3, 20, 30, 40, *scale])
    result = scene.surface_normal(session.engine, mesh.handle, matrix, 0)
    expected = np.linalg.inv(np.array(matrix).reshape(4, 4)[:3, :3]).T @ [-1, 0, 1]
    assert result == pytest.approx(expected / np.linalg.norm(expected))
    hit = offset_hit(dict(point=[1, 2, 3], normal=result), -0.02)
    assert hit["point"] == pytest.approx(np.array([1, 2, 3]) - 0.02 * np.array(result))
    assert hit["surface"] == [1, 2, 3]


def free_curve(session):
    entity = session.command("primitive.create", kind="BODY")
    curve = session.document.object(session.document.entity(entity).primitive.curves[0].id)
    session.command(
        "point.update",
        entity=entity,
        curve=curve.id,
        point=curve.points[0].id,
        left=[-0.7, 0, 0],
        right=[-0.3, 0, 0],
        left_mode="FREE",
        right_mode="FREE",
    )
    return entity


def transform_editor(session):
    entity = free_curve(session)
    item = session.document.entity(entity)
    rows = authoring_state.curve_components(
        session, item, session.document.object(item.primitive.curves[0].id)
    )
    controller = SimpleNamespace(session=session, selection=entity, refresh=lambda: None)
    return SimpleNamespace(
        controller=controller,
        rows=rows,
        state={},
        selection=[authoring_state.component_key(rows[1][0])],
        transformData=dict(trs=[*rows[1][1], 0, 0, 0, 1, 1, 1]),
    )


@pytest.mark.parametrize(
    "mode,delta", [("Rotate", [0, 0, 0, 0, 0, 90, 1, 1, 1]), ("Scale", [0, 0, 0, 0, 0, 0, 2, 2, 2])]
)
def test_selected_curve_point_transforms_its_handles(session, mode, delta):
    from anthroforge.desktop.transform_delta import matrix

    editor = transform_editor(session)
    before = session.document
    authoring_actions.start_transform(editor, mode)
    assert len(editor.drag_rows) == 3
    transform = matrix(session.engine, editor.drag_center, delta)
    expected = session.engine.world_point(transform, editor.rows[2][1])
    authoring_actions.apply_delta(editor, delta)
    use = session.document.entity(editor.controller.selection).primitive.curves[0]
    point = session.document.object(use.id).points[0]
    assert point.right == pytest.approx(expected)
    session.command("cancel")
    assert session.document.entities == before.entities
