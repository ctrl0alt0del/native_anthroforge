"""Skin eligibility is read-only, operation-specific and shared with the API."""

from dataclasses import replace

import pytest

from tests.test_skin_reference import build, topology


def test_empty_status_does_not_initialize_native_or_mutate_session(session):
    before, history = session.document, tuple(session.history.entries)
    engine = session._engine
    first = session.skin_status.snapshot()
    assert session.skin_status.snapshot() is first
    assert not first.operations["fit"].available and not first.operations["export"].available
    assert session.document is before and tuple(session.history.entries) == history
    assert session._engine is engine and not session.scheduler.blocked
    with pytest.raises(ValueError, match="reference"):
        session.command("skin.evaluate")


def test_usable_reference_with_stale_settings_warns_but_allows_fitting(session):
    topology(session)
    build(session)
    assert session.command("skin.status")["operations"]["fit"]["available"]
    session.command("skin.configure", section="envelope_settings", values={"gap_strength": 0.25})
    status = session.skin_status.snapshot()
    assert status.operations["fit"].available and status.operations["fit"].warnings
    assert status.operations["export"].available and status.operations["export"].warnings


def test_missing_reference_blocks_fitting_and_status_subscribers_are_notified(session):
    topology(session)
    skin = build(session)
    changes = []
    stop = session.skin_status.subscribe(lambda: changes.append(session.document.revision))
    session.replace_document(skin=replace(skin, reference="missing"))
    status = session.skin_status.snapshot()
    assert changes and not status.operations["fit"].available
    assert status.operations["export"].available
    stop()
    session.replace_document(skin=skin)
    assert len(changes) == 1 and session.skin_status.snapshot().operations["fit"].available
