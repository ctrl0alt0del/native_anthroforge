"""Inflation preview never becomes authored state, an accepted surface or a save blocker."""

import pytest

from anthroforge.application import storage
from tests.test_tissue_workflow import assembly


def ready(session, target, **options):
    session.command("tissue.preview", target=target, **options)
    session.wait(20)
    value = session.command("tissue.preview.status")
    assert value["state"] == "ready", value
    return value


def test_preview_cancel_and_save_leave_authored_geometry_and_history_unchanged(session, tmp_path):
    _, _, target = assembly(session)
    before, cursor = session.document, session.history.cursor
    ready(session, target, changes=dict(amount=0.15))
    assert session.document == before and session.history.cursor == cursor
    assert (
        session.tissue_preview.asset.mesh.handle
        != session.assets[before.object(target).result.asset].mesh.handle
    )
    location = tmp_path / "preview.anthroforge"
    session.command("save", path=str(location), blocked_policy="wait")
    document, _ = storage.read_package(location, session.engine)
    assert document.object(target) == before.object(target)
    session.command("tissue.preview.cancel")
    assert session.tissue_preview.asset is None and not session.scheduler.blocked


def test_accept_is_one_undo_action_and_uses_shared_inflation_policy(session):
    _, _, target = assembly(session)
    before, cursor = session.document.object(target), session.history.cursor
    settings = dict(amount=0.07, mode="SECTION_PROFILE")
    value = ready(session, target, changes=settings, reset="PROFILE")
    session.command("tissue.preview.accept", token=value["token"])
    session.wait(20)
    item = session.document.object(target)
    assert (
        item.parts[0].a.inflation.amount == 0.07 and item.parts[0].a.inflation.profile.initialized
    )
    assert session.history.cursor == cursor + 1 and session.tissue_preview.asset is None
    session.command("undo")
    session.wait(20)
    assert session.document.object(target).parts == before.parts


def test_changed_source_rejects_stale_preview_and_cancel_releases_candidate(session):
    _, _, target = assembly(session)
    value = ready(session, target, changes=dict(amount=0.08))
    session.command("tissue.inflation", target=target, changes=dict(amount=0.04))
    session.wait(20)
    assert session.command("tissue.preview.status")["state"] == "stale"
    with pytest.raises(ValueError, match="current successful"):
        session.command("tissue.preview.accept", token=value["token"])
    session.command("tissue.preview.cancel")
    assert session.tissue_preview.asset is None


def test_repeated_preview_and_initialization_never_commit_intermediate_settings(session):
    _, _, target = assembly(session)
    before = session.document.object(target)
    session.command("tissue.preview", target=target, changes=dict(amount=0.03))
    value = ready(session, target, changes=dict(mode="CTRL_POINT"), reset="CONTROL")
    assert len(value["settings"]["control"]) == 3
    assert session.document.object(target) == before
    assert not session.scheduler.blocked


def test_accepting_unchanged_preview_preserves_inactive_mode_settings(session):
    _, _, target = assembly(session)
    before = session.document.object(target)
    value = ready(session, target, changes={})
    session.command("tissue.preview.accept", token=value["token"])
    session.wait(20)
    assert session.document.object(target).parts == before.parts
