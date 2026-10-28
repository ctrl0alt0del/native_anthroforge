"""Fitting obeys cancellation, history and captured-input publication contracts."""

from dataclasses import asdict
from threading import Event

from anthroforge.application import skin_fit_evaluation
from anthroforge.application.skin_results import ComputedStage
from tests.test_skin_fit_jobs import fit, setup


def controlled(session, monkeypatch):
    identity = setup(session)
    item = fit(session, identity)
    result = ComputedStage(session.assets[item.reference].mesh, session.resources.skin[item.data])
    session.command("skin.fit.remove", identity=item.id)
    entered, release = Event(), Event()

    def compute(*args):
        entered.set()
        assert release.wait(10)
        return result

    monkeypatch.setattr(skin_fit_evaluation, "evaluate", compute)
    return identity, entered, release


def start(session, identity, entered):
    key = session.command(
        "skin.fit", shortcut=identity, settings=dict(minimum=0, maximum=0.2, bones=1, samples=5)
    )
    session.scheduler.tick()
    assert entered.wait(10)
    return key


def test_cancelled_fit_never_publishes_and_redo_restarts(session, monkeypatch):
    identity, entered, release = controlled(session, monkeypatch)
    key = start(session, identity, entered)
    try:
        session.command("job.cancel", job_id=key)
    finally:
        release.set()
    session.wait()
    assert session.scheduler.registry.by_id[key].state == "cancelled"
    assert not session.document.skin.fits
    session.command("undo")
    session.command("redo")
    session.wait()
    assert len(session.document.skin.fits) == 1


def test_undo_during_fit_keeps_original_checkpoint(session, monkeypatch):
    identity, entered, release = controlled(session, monkeypatch)
    before = session.document
    start(session, identity, entered)
    try:
        assert session.scheduler.checkpoint.skin == before.skin
        session.command("undo")
    finally:
        release.set()
    session.wait()
    assert not session.document.skin.fits
    session.command("redo")
    session.wait()
    assert len(session.document.skin.fits) == 1


def test_source_edit_discards_obsolete_fit_and_records_latest_provenance(session, monkeypatch):
    identity, entered, release = controlled(session, monkeypatch)
    key = start(session, identity, entered)
    try:
        reference = asdict(session.document.shortcuts[0].reference)
        session.command("shortcut.set", reference=reference, value=0.1)
    finally:
        release.set()
    session.wait()
    assert session.scheduler.registry.by_id[key].obsolete
    assert len(session.document.skin.fits) == 1
    item = session.document.skin.fits[0]
    assert not session.command("skin.fit.inspect", identity=item.id)["stale"]
