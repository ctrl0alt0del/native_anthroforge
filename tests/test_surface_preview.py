"""Alignment previews are owned candidates, never implicitly committed construction."""

import pytest

from anthroforge.application import storage
from anthroforge.core.surfaces import Surface


def loops(session):
    points = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    curves = [
        session.command(
            "curve.create",
            engine="POLYLINE",
            closed=True,
            points=[dict(position=[x, y, z]) for x, y in points],
        )
        for z in (0, 1)
    ]
    session.wait(5)
    return curves


def preview(session, **args):
    result = session.command("surface.preview", **args)
    session.wait(5)
    status = session.command("surface.preview.status")
    assert status["state"] == "ready", status
    return result["token"]


def test_alignment_preview_does_not_edit_save_or_history(session, tmp_path):
    curves = loops(session)
    before, undo = session.document, session.history.cursor
    token = preview(session, curves=curves)
    assert session.document == before and session.history.cursor == undo
    path = tmp_path / "preview.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    saved, _ = storage.read_package(path, session.engine)
    assert not any(isinstance(item, Surface) for item in saved.objects)
    key = session.command("surface.preview.accept", token=token)
    assert session.document.object(key).result.status == "ready"
    assert session.history.cursor == undo + 1
    session.command("undo")
    assert key not in session.document.registry.records


def test_changed_source_cannot_accept_stale_geometry(session):
    curves = loops(session)
    token = preview(session, curves=curves)
    point = session.document.object(curves[0]).points[0].id
    session.command("curve.point.update", curve=curves[0], point=point, position=[-2, -1, 0])
    session.wait(5)
    assert session.command("surface.preview.status")["state"] == "stale"
    with pytest.raises(ValueError, match="current successful"):
        session.command("surface.preview.accept", token=token)
    session.command("surface.preview.cancel")
    assert session.surface_preview.asset is None


def test_realign_preview_preserves_metadata_and_commits_one_undo(session):
    curves = loops(session)
    key = session.command("surface.preview.accept", token=preview(session, curves=curves))
    before = session.document.object(key)
    token = preview(session, target=key)
    assert session.document.object(key) == before
    session.command("object.rename", target=key, name="Renamed")
    undo = session.history.cursor
    session.command("surface.preview.accept", token=token)
    assert session.document.object(key).name == "Renamed" and session.history.cursor == undo + 1
    session.command("undo")
    assert session.document.object(key).result == before.result


def test_preview_tracks_ordinary_parent_frame(session):
    parent = session.command("scp.empty", name="Frame")
    token = preview(session, curves=loops(session), parent=parent)
    session.command("scp.transform", entity=parent, values=[1, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait(5)
    with pytest.raises(ValueError, match="current successful"):
        session.command("surface.preview.accept", token=token)


def test_cancelled_preview_does_not_create_objects_or_block_save(session):
    curves = loops(session)
    before = session.document
    session.command("surface.preview", curves=curves)
    session.command("surface.preview.cancel")
    session.wait(5)
    assert session.document == before and session.surface_preview.asset is None
    assert not session.scheduler.blocked


def test_deleted_source_invalidates_preview_without_status_failure(session):
    curves = loops(session)
    preview(session, curves=curves)
    session.command("object.delete", target=curves[0])
    assert session.command("surface.preview.status")["state"] == "stale"
