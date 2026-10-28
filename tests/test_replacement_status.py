"""Status reads and replacement execution share target, workspace and lifecycle policy."""

import pytest

from tests.conftest import CUBE
from tests.test_mesh_replacement import assessment, source


def status(session, target):
    return session.command("scp.mesh.replace.eligibility", target=target)


def test_status_is_readonly_without_native_initialization(session):
    before, history = session.document, tuple(session.history.entries)
    assert not status(session, "")["start"]["available"]
    assert not session.command("tissue.source.replace.eligibility", target="")["start"]["available"]
    assert session.document is before and tuple(session.history.entries) == history
    assert session._engine is None and not session.scheduler.blocked


def assert_blocked(session, target):
    result = status(session, target)["start"]
    assert not result["available"]
    with pytest.raises(ValueError) as error:
        session.command("scp.mesh.replace.assess", target=target, path=str(CUBE))
    assert str(error.value) == result["reason"]


def test_start_tracks_gesture_save_and_workspace(session, assembly):
    root, child = assembly
    assert status(session, root)["start"]["available"]
    session.begin()
    assert_blocked(session, root)
    session.cancel()
    session.waiting_save = True
    assert_blocked(session, root)
    session.waiting_save = False
    session.command("workspace.create", name="Child", members=[child])
    assert_blocked(session, root)
    assert status(session, child)["start"]["available"]


def test_apply_status_tracks_review_and_staleness(session):
    target = source(session)
    assert not status(session, target)["apply"]["available"]
    token, _ = assessment(session, target, CUBE)
    assert status(session, target)["apply"]["available"]
    session.command("scp.rename", entity=target, name="Changed")
    result = status(session, target)["apply"]
    assert not result["available"]
    with pytest.raises(ValueError) as error:
        session.command("scp.mesh.replace.apply", token=token)
    assert str(error.value) == result["reason"]


def test_tissue_status_uses_same_guard_as_retarget(session):
    from tests.test_tissue_workflow import assembly

    _, source_id, target = assembly(session)
    assert session.command("tissue.source.replace.eligibility", target=target)["start"]["available"]
    session.begin()
    result = session.command("tissue.source.replace.eligibility", target=target)["start"]
    with pytest.raises(ValueError) as error:
        session.command("tissue.source.replace.assess", target=target, source=source_id)
    assert not result["available"] and str(error.value) == result["reason"]
    session.cancel()
