from dataclasses import replace
from threading import Event

import pytest

from anthroforge.application import importing
from anthroforge.application.storage import FileLock, atomic_save, read_package


def test_child_edit_survives_queued_parent_motion(assembly, session):
    root, child = assembly
    session.command("scp.transform", entity=child, values=[2, 0, 0, 0, 0, 0, 0.2, 0.2, 0.2])
    session.command("scp.transform", entity=root, values=[0, 0, 3, 0, 0, 0, 1, 1, 1])
    session.command("wait")
    position = session.engine.decompose(session.document.entity(child).matrix)[:3]
    assert position == pytest.approx([2, 0, 3])


def test_per_scp_on_release_updates_descendants(assembly, session):
    root, child = assembly
    session.command("update_mode", entity=root, mode="ON_RELEASE")
    session.command("begin")
    session.command("scp.transform", entity=root, values=[0, 0, 2, 0, 0, 0, 1, 1, 1])
    assert not session.scheduler.blocked
    session.command("commit")
    session.command("wait")
    assert session.document.entity(child).matrix[11] == pytest.approx(2)


def test_failed_anchor_is_saved_and_can_be_repaired(assembly, session, tmp_path):
    root, child = assembly
    session.command("scp.attachment", entity=child, face_lock=9999)
    session.command("wait")
    assert session.document.entity(child).status == "failed"
    path = tmp_path / "failed.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    document, _ = read_package(path, session.engine)
    assert document.entity(child).status == "failed"
    session.command("scp.attachment", entity=child, face_lock=-1)
    session.command("wait")
    assert session.document.entity(child).status == "ready"


def test_workspace_survives_anatomical_undo(assembly, session):
    root, child = assembly
    session.command("scp.rename", entity=child, name="Changed")
    session.command("workspace.create", name="Child", members=[child])
    session.command("undo")
    assert session.workspace.name == "Child"
    assert session.document.entity(child).name != "Changed"


def test_rename_and_color_survive_calculation_publication(assembly, session):
    root, child = assembly
    session.command("scp.transform", entity=root, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    session.scheduler.tick()
    session.command("scp.rename", entity=child, name="User name")
    session.command("scp.color", entity=child, value="#aabbcc")
    session.command("wait")
    assert session.document.entity(child).name == "User name"
    assert session.document.entity(child).color == "#aabbcc"


def blocked_import(monkeypatch):
    original, gate = importing.imported, Event()

    def delayed(*args):
        assert gate.wait(3)
        return original(*args)

    monkeypatch.setattr(importing, "imported", delayed)
    return gate


def test_import_undo_redo_restarts_once(session, monkeypatch):
    gate = blocked_import(monkeypatch)
    result = session.command("import", path="examples/primitives/cube.obj", units=1)
    session.scheduler.tick()
    session.command("undo")
    session.command("redo")
    gate.set()
    session.command("wait")
    assert [e.id for e in session.document.entities] == [result["entity_id"]]
    assert any(job.state == "obsolete" for job in session.scheduler.jobs)


def test_import_can_publish_while_modal_wait_blocks_editing(session):
    session.command("import", path="examples/primitives/cube.obj", units=1)
    session.waiting_save = True
    session.command("wait")
    assert len(session.document.entities) == 1


def test_failed_atomic_write_preserves_previous_file(assembly, session, tmp_path, monkeypatch):
    path = tmp_path / "safe.anthroforge"
    atomic_save(path, session.document, session.resources)
    before = path.read_bytes()
    monkeypatch.setattr("anthroforge.application.storage.write_package", corrupt_write)
    with pytest.raises(OSError):
        atomic_save(path, replace(session.document, name="New"), session.resources)
    assert path.read_bytes() == before
    FileLock(path).close()


def corrupt_write(path, document, assets, cancel=None, recovery=None):
    path.write_bytes(b"incomplete")
    raise OSError("Injected disk failure")
