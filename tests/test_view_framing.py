import numpy as np

from anthroforge.desktop.controller_actions import frame_bounds
from anthroforge.native import scene


def imported_child(session, parent):
    result = session.command("import", path="examples/primitives/cube.obj", units=1, parent=parent)
    session.command("wait", timeout=5)
    return result["entity_id"]


def test_empty_group_frames_only_visible_descendant_geometry(session):
    root = session.command("scp.empty", name="Group")
    imported_child(session, root)
    far = imported_child(session, root)
    session.command("scp.transform", entity=far, values=[8, -3, 2, 0, 0, 0, 1, 1, 1])
    session.command("wait", timeout=5)
    center, radius = frame_bounds(session, session.document.entity(root), [1, 1, 1])
    np.testing.assert_allclose(center, [4, -1.5, 1])
    assert radius == 9
    session.command("workspace.update", hidden=[far])
    center, radius = frame_bounds(session, session.document.entity(root), [1, 1, 1])
    np.testing.assert_allclose(center, [0, 0, 0])
    assert radius == 1


def test_scene_bounds_include_rotation_reflection_and_geometry_offset(session):
    entity = imported_child(session, "")
    mesh = session.assets[session.document.entity(entity).asset].mesh
    matrix = session.engine.transform([3, 4, 5, 0, 0, 90, -2, 4, 1])
    frame = scene.geometry_matrix(session.engine, matrix, [1, 0, 0])
    bounds = scene.bounds(session.engine, [mesh.handle], [frame])
    np.testing.assert_allclose(bounds, [1, 1, 4.5, 5, 3, 5.5], atol=1e-7)
