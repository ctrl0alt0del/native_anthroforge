import pytest

from anthroforge.application.session import Session
from anthroforge.core.entities import descendants


def move(session, entity, x=0.0, y=0.0, z=0.0, rotation=0.0, scale=1.0):
    session.command(
        "scp.transform", entity=entity, values=[x, y, z, 0, 0, rotation, scale, scale, scale]
    )
    session.command("wait")


def test_cube_canonical_polygons(session, assembly):
    root, _ = assembly
    mesh = session.assets[session.document.entity(root).asset].mesh
    assert mesh.counts[:4] == (8, 6, 24, 12)
    assert mesh.bounds == (-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)


def test_child_follows_parent_and_undo_redo(session, assembly):
    root, child = assembly
    move(session, root, z=2.0)
    assert session.document.entity(child).matrix[11] == pytest.approx(2.0)
    session.command("undo")
    assert session.document.entity(child).matrix[11] == pytest.approx(0.0)
    session.command("redo")
    assert session.document.entity(child).matrix[11] == pytest.approx(2.0)


@pytest.mark.parametrize("parent_mode", ["OBJECT_ORIGIN", "SURFACE_NEAREST"])
@pytest.mark.parametrize("child_mode", ["OBJECT_ORIGIN", "FACE_CENTER", "VERTEX_NEAREST"])
@pytest.mark.parametrize("strategy", ["AUTO", "STABLE_SURFACE", "DEFORMATION_FLOW"])
def test_attachment_modes_preserve_capture_pose(
    session, assembly, parent_mode, child_mode, strategy
):
    root, child = assembly
    before = session.document.entity(child).matrix
    settings = dict(parent_mode=parent_mode, child_mode=child_mode, strategy=strategy)
    session.command("scp.attachment", entity=child, **settings)
    session.command("wait")
    assert session.document.entity(child).matrix == pytest.approx(before)
    move(session, root, z=2.0)
    assert session.document.entity(child).matrix[11] == pytest.approx(2.0)


def test_rotation_follow_can_be_disabled(session, assembly):
    root, child = assembly
    session.command("scp.attachment", entity=child, follow_rotation=False)
    session.command("wait")
    move(session, root, rotation=90.0)
    values = session.engine.decompose(session.document.entity(child).matrix)
    assert values[3:6] == pytest.approx([0, 0, 0])


def test_anchor_lock_and_origin_move(session, assembly):
    _, child = assembly
    session.command("scp.attachment", entity=child, child_mode="VERTEX_NEAREST", vertex_lock=3)
    session.command("wait")
    item = session.document.entity(child)
    assert item.attachment.binding[27] == 3
    before = session.engine.world_point(item.matrix, item.geometry_offset)
    session.command("scp.origin", entity=child)
    session.command("wait")
    item = session.document.entity(child)
    assert session.engine.world_point(item.matrix, item.geometry_offset) == pytest.approx(before)
    assert item.attachment.binding[18:21] == pytest.approx([0, 0, 0])


def test_toggle_rebinds_current_pose(session, assembly):
    root, child = assembly
    session.command("attachments.enable", enabled=False)
    move(session, root, z=2.0)
    assert session.document.entity(child).matrix[11] == 0.0
    session.command("attachments.enable", enabled=True)
    session.command("wait")
    assert session.document.entity(child).matrix[11] == pytest.approx(0.0)
    move(session, root, z=3.0)
    assert session.document.entity(child).matrix[11] == pytest.approx(1.0)


def test_manual_update_does_not_recapture_descendants(session, assembly):
    root, child = assembly
    session.command("update_mode", mode="MANUAL")
    move(session, root, z=2.0)
    assert session.document.entity(child).matrix[11] == 0.0
    session.command("evaluate")
    session.command("wait")
    assert session.document.entity(child).matrix[11] == pytest.approx(2.0)


def test_on_release_is_one_undo_step(session, assembly):
    root, child = assembly
    session.command("update_mode", mode="ON_RELEASE")
    session.command("begin")
    session.command("scp.transform", entity=root, values=[0, 0, 2, 0, 0, 0, 1, 1, 1])
    assert session.document.entity(child).matrix[11] == 0.0
    session.command("commit")
    session.command("wait")
    assert session.document.entity(child).matrix[11] == pytest.approx(2.0)
    session.command("undo")
    assert session.document.entity(root).matrix[11] == 0.0


def test_focused_workspace_preserves_outside_dependencies(session, assembly):
    root, child = assembly
    session.command("workspace.create", name="Child", members=[child])
    with pytest.raises(ValueError, match="read-only"):
        session.command("scp.transform", entity=root, values=[0, 0, 2, 0, 0, 0, 1, 1, 1])
    move(session, child, x=2.0)
    assert session.document.entity(child).parent == root


def test_duplicate_remaps_and_cycle_is_rejected(session, assembly):
    root, child = assembly
    copy = session.command("scp.duplicate", entity=child)
    session.command("wait")
    assert copy != child
    assert session.document.entity(copy).parent == root
    with pytest.raises(ValueError, match="cycle"):
        session.command("scp.reparent", entity=child, parent=child)
    assert descendants(session.document.entities, root) == {root, child, copy}


def test_portable_project_and_no_persisted_undo(session, assembly, tmp_path):
    path = tmp_path / "assembly.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    expected = session.document.entities
    session.close()
    other = Session()
    try:
        other.command("open", path=str(path))
        other.command("wait")
        assert [e.matrix for e in other.document.entities] == [e.matrix for e in expected]
        assert len(other.history.entries) == 1
    finally:
        other.close()


def test_second_writer_rejected(session, assembly, tmp_path):
    path = tmp_path / "assembly.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    other = Session()
    try:
        with pytest.raises(ValueError, match="already open"):
            other.command("open", path=str(path))
    finally:
        other.close()
