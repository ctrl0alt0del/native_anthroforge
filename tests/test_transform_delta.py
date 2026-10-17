import numpy as np
import pytest

from anthroforge.desktop.transform_delta import matrix, object_values


def test_world_rotation_preserves_pivot_and_existing_scale(session):
    original = [2, 3, 4, 25, 35, 45, 2, 3, 4]
    values = object_values(session.engine, original, [0, 0, 0, 0, 0, 90, 1, 1, 1])
    assert values[:3] == pytest.approx(original[:3])
    assert values[6:] == pytest.approx(original[6:])
    before = np.array(session.engine.transform(original)).reshape(4, 4)
    after = np.array(session.engine.transform(values)).reshape(4, 4)
    rotation = np.array(session.engine.transform([0, 0, 0, 0, 0, 90, 1, 1, 1])).reshape(4, 4)
    assert after[:3, :3] == pytest.approx(rotation[:3, :3] @ before[:3, :3])


def test_local_scale_preserves_rotation_and_reflection(session):
    original = [2, 3, 4, 25, 35, 45, -2, -3, -4]
    values = object_values(session.engine, original, [0, 0, 0, 0, 0, 0, 1.5, 1, 1])
    expected = [*original[:6], -3, -3, -4]
    assert session.engine.transform(values) == pytest.approx(session.engine.transform(expected))


def test_component_rotation_uses_selection_pivot(session):
    delta = matrix(session.engine, [2, 3, 4], [0, 0, 0, 0, 0, 90, 1, 1, 1])
    assert session.engine.world_point(delta, [3, 3, 4]) == pytest.approx([2, 4, 4])
