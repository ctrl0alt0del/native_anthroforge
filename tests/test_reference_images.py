"""Image assignments share assets, not authored placement or calibration."""

from threading import Event

import pytest
from PIL import Image

from anthroforge.application import image_tasks, storage
from anthroforge.application.curve_sources import world
from anthroforge.native.strokes import plane


def source(tmp_path, name="reference.png", size=(512, 300)):
    path = tmp_path / name
    Image.new("RGB", size, "red").save(path)
    return str(path)


def loaded(session, path, **options):
    result = session.command("image.import", path=path, **options)
    session.command("wait")
    return result["object_id"]


@pytest.mark.parametrize("axis, normal", [("X", [1, 0, 0]), ("Y", [0, 1, 0]), ("Z", [0, 0, 1])])
def test_parented_import_aligns_in_world_space_in_one_undo(session, tmp_path, axis, normal):
    root = session.command("scp.empty", name="Parent")
    session.command("scp.transform", entity=root, values=[2, 3, 4, 30, 50, 20, 2, 3, 4])
    before = session.history.cursor
    target = loaded(session, source(tmp_path), parent=root, owner=root, axis=axis)
    item = session.document.object(target)
    assert item.parent == root and item.owners == (root,)
    assert plane(session.engine, world(session.engine, session.document, target)) == pytest.approx(
        [2, 3, 4, *normal], abs=1e-10
    )
    assert session.history.cursor == before + 1
    session.command("undo")
    assert target not in session.document.registry.records
    session.command("redo")
    assert session.document.object(target) == item


def test_invalid_import_axis_rejects_before_scheduling(session, tmp_path):
    before, jobs = session.history.cursor, len(session.scheduler.jobs)
    with pytest.raises(ValueError, match="requires X, Y or Z"):
        loaded(session, source(tmp_path), axis="OTHER")
    assert session.history.cursor == before and len(session.scheduler.jobs) == jobs


def test_image_cannot_be_imported_under_readonly_parent(session, assembly, tmp_path):
    root, child = assembly
    session.command("workspace.create", name="Child", members=[child])
    with pytest.raises(ValueError, match="outside the focused workspace"):
        loaded(session, source(tmp_path), parent=root)


def test_image_only_document_and_shared_instance(session, tmp_path):
    target = loaded(session, source(tmp_path), width=2)
    copy = session.command("image.instance", source=target)
    assert not session.document.entities and len(session.document.objects) == 2
    assert session.document.object(copy).source == session.document.object(target).source
    asset = next(iter(session.resources.images.values()))
    assert asset.texture.chunks == 4
    assert session.command("image.inspect", target=target)["dimensions"] == [2, 300 / 256]
    session.command("image.size", target=copy, width=4)
    assert session.document.object(target).width == 2
    assert session.document.object(copy).width == 4


def test_calibration_uses_world_distance_and_one_undo(session, tmp_path):
    target = loaded(session, source(tmp_path), values=[0, 0, 0, 0, 0, 0, 2, 3, 1])
    before, cursor = session.document.object(target), session.history.cursor
    session.command("image.calibrate", target=target, first=[0, 0], second=[1, 0], distance=8)
    changed = session.document.object(target)
    assert changed.width == 4 and changed.height == before.height * 4
    assert session.history.cursor == cursor + 1
    session.command("undo")
    assert session.document.object(target) == before
    session.command("redo")
    assert session.document.object(target) == changed


def test_replacement_preserves_instance_width_and_pose_and_calibration_undo(session, tmp_path):
    target = loaded(session, source(tmp_path))
    session.command("image.calibrate", target=target, first=[0, 0], second=[1, 0], distance=2)
    original = session.document.object(target)
    copy = session.command("image.instance", source=target)
    session.command("image.replace", target=target, path=source(tmp_path, "tall.png", (50, 100)))
    session.command("wait")
    changed = session.document.object(target)
    assert (changed.width, changed.height, changed.matrix) == (2, 4, original.matrix)
    assert changed.calibration is None and session.document.object(copy).source == original.source
    session.command("undo")
    assert session.document.object(target) == original
    session.command("redo")
    assert session.document.object(target) == changed and not session.scheduler.blocked


def delayed_decode(monkeypatch):
    original, gate = image_tasks.decode, Event()

    def delayed(*args):
        assert gate.wait(4)
        return original(*args)

    monkeypatch.setattr(image_tasks, "decode", delayed)
    return gate


def test_image_import_remains_at_initiating_undo_step(session, tmp_path, monkeypatch):
    gate = delayed_decode(monkeypatch)
    target = session.command("image.import", path=source(tmp_path))["object_id"]
    session.scheduler.tick()
    curve = session.command("curve.create")
    gate.set()
    session.command("wait")
    session.command("undo")
    assert target in session.document.registry.records
    assert curve not in session.document.registry.records
    session.command("undo")
    assert not session.document.objects
    session.command("redo")
    assert target in session.document.registry.records and not session.scheduler.blocked


def test_pending_image_import_undo_redo_restarts(session, tmp_path, monkeypatch):
    gate = delayed_decode(monkeypatch)
    target = session.command("image.import", path=source(tmp_path))["object_id"]
    session.scheduler.tick()
    session.command("undo")
    session.command("redo")
    gate.set()
    session.command("wait")
    assert [o.id for o in session.document.objects] == [target]
    assert any(job.state == "obsolete" for job in session.scheduler.jobs)


def test_same_source_replacement_is_not_restarted_after_redo(session, tmp_path):
    path = source(tmp_path)
    target = loaded(session, path)
    session.command("image.replace", target=target, path=path)
    session.command("wait")
    session.command("undo")
    session.command("redo")
    assert not session.scheduler.blocked


def test_embedded_image_reopens_without_original_file(session, tmp_path):
    path = tmp_path / "reference.png"
    target = loaded(session, source(tmp_path))
    project = tmp_path / "image.anthroforge"
    storage.atomic_save(project, session.document, session.resources)
    path.unlink()
    document, resources = storage.read_package(project, session.engine)
    assert document.object(target) == session.document.object(target)
    assert next(iter(resources.images.values())).texture.chunks == 4


def test_invalid_image_does_not_publish_partial_object(session, tmp_path):
    path = tmp_path / "broken.png"
    path.write_bytes(b"broken")
    session.command("image.import", path=str(path))
    session.command("wait")
    assert not session.document.objects and not session.resources.images
    assert next(j for j in session.scheduler.jobs if j.kind == "image_decode").state == "failed"


def test_image_cannot_be_parent_and_bad_landmarks_are_rejected(session, tmp_path):
    target = loaded(session, source(tmp_path))
    with pytest.raises(ValueError, match="cannot be a reference image"):
        session.command("curve.create", parent=target)
    with pytest.raises(ValueError, match="normalized 2D"):
        session.command("image.calibrate", target=target, first=[0], second=[1, 0], distance=2)
    with pytest.raises(ValueError, match="within the image"):
        session.command("image.calibrate", target=target, first=[-1, 0], second=[1, 0], distance=2)
