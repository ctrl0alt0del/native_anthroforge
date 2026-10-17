import pytest

from anthroforge.core.entities import validate_tree
from anthroforge.core.jobs import Job


def test_delete_promotes_children_without_moving_them(session, assembly):
    root, child = assembly
    leaf = session.command("scp.empty", name="Leaf", parent=child)
    session.wait()
    before = session.document.entity(leaf).matrix
    session.command("scp.delete", entity=child)
    session.wait()
    assert session.document.entity(leaf).parent == root
    assert session.document.entity(leaf).matrix == pytest.approx(before)
    validate_tree(session.document.entities)
    session.command("undo")
    assert session.document.entity(leaf).parent == child
    session.command("redo")
    assert session.document.entity(leaf).parent == root


def test_delete_root_replaces_with_group_and_preserves_children(session, assembly):
    root, child = assembly
    before = session.document.entity(child).matrix
    replacement = session.command("scp.delete", entity=root)
    session.wait()
    assert replacement != root
    assert session.document.entity(replacement).primitive is None
    assert session.document.entity(child).parent == replacement
    assert session.document.entity(child).matrix == pytest.approx(before)
    validate_tree(session.document.entities)
    session.command("undo")
    assert session.document.entity(child).parent == root


def test_delete_in_focused_workspace_preserves_external_children(session, assembly):
    root, child = assembly
    session.command("workspace.create", name="Root only", members=[root], children=False)
    replacement = session.command("scp.delete", entity=root)
    session.wait()
    assert session.document.entity(child).parent == replacement
    assert replacement in session.workspace.members
    session.command("undo")
    assert session.editable(root)


def test_delete_leaf_root_leaves_valid_empty_document(session):
    root = session.command("scp.empty", name="Root")
    session.command("scp.delete", entity=root)
    assert not session.document.entities
    validate_tree(session.document.entities)
    session.command("undo")
    assert session.document.entity(root)


def test_delete_readonly_scp_is_rejected(session, assembly):
    root, child = assembly
    session.command("workspace.create", name="Child only", members=[child], children=False)
    with pytest.raises(ValueError, match="read-only"):
        session.command("scp.delete", entity=root)
    assert session.document.entity(child).parent == root


def test_delete_rejects_obsolete_publication(session, assembly):
    root, child = assembly
    published = []
    job = waiting_job(child, published)
    session.scheduler.submit(job)
    session.scheduler.tick()
    session.command("scp.delete", entity=child)
    session.wait(timeout=5)
    assert job.obsolete and not published
    assert len(session.document.entities) == 1
    assert session.document.entity(root)


def test_promoted_child_follows_new_parent_after_recapture(session, assembly):
    root, child = assembly
    leaf = session.command("scp.empty", name="Leaf", parent=child)
    session.wait()
    session.command("scp.delete", entity=child)
    session.wait()
    before = session.engine.decompose(session.document.entity(leaf).matrix)
    session.command("scp.transform", entity=root, values=[2, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait()
    after = session.engine.decompose(session.document.entity(leaf).matrix)
    assert after[0] == pytest.approx(before[0] + 2)


def waiting_job(child, published):
    return Job(
        "Old child work",
        frozenset({child}),
        lambda d: d,
        lambda payload, cancel: cancel.wait(2),
        published.append,
    )


def test_delete_during_child_construction_finishes_surviving_geometry(session):
    root = session.command("scp.empty", name="Root")
    parent = session.command("scp.empty", name="Parent", parent=root)
    child = session.command("primitive.create", kind="LOFT", parent=parent)
    session.wait()
    session.command("primitive.update", entity=child, samples=96)
    session.command("scp.delete", entity=parent)
    session.wait(timeout=5)
    assert session.document.entity(child).parent == root
    assert session.document.entity(child).result.status == "ready"
    assert session.assets[session.document.entity(child).asset].mesh.counts[0] == 192
    assert not session.scheduler.errors


def test_delete_and_save_reopen_preserves_promoted_structure(session, assembly, tmp_path):
    root, child = assembly
    replacement = session.command("scp.delete", entity=root)
    session.wait()
    path = str(tmp_path / "promoted.anthroforge")
    session.command("save", path=path, blocked_policy="wait")
    session.wait()
    session.command("open", path=path)
    session.wait()
    assert session.document.entity(child).parent == replacement
    assert session.document.entity(replacement).primitive is None
