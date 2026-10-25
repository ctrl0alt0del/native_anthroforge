"""Recovery captures preserve committed revisions, active gestures and file ownership."""

from pathlib import Path
from threading import Event
from time import monotonic, sleep

import pytest

from anthroforge.application.autosave import Autosave
from anthroforge.application.recovery import KEEP, RecoveryStore
from anthroforge.application.storage import atomic_save, read_package
from anthroforge.core.jobs import Job


def service(session, tmp_path):
    now = [0.0]
    saver = Autosave(RecoveryStore(tmp_path / "Autosaves"), clock=lambda: now[0])
    saver.poll(session)
    return saver, now


def advance(session, saver, now):
    now[0] += 301
    saver.poll(session)
    session.wait(5)
    assert saver.job is None, saver.error


def test_autosave_roundtrip_retains_dirty_history_and_untitled_path(session, tmp_path):
    saver, now = service(session, tmp_path)
    session.command("scp.empty", name="Recovery anatomy")
    before, cursor = session.document, session.history.cursor
    advance(session, saver, now)
    rows, unreadable = saver.store.scan()
    document, _ = read_package(Path(rows[0]["path"]), session.engine)
    assert document == before and not unreadable and rows[0]["origin"] == ""
    assert session.document is before and session.history.cursor == cursor
    assert session.path is None and session.saved_revision == 0
    advance(session, saver, now)
    assert len(saver.store.scan()[0]) == 1


def test_autosave_does_not_commit_or_capture_provisional_gesture(session, tmp_path):
    saver, now = service(session, tmp_path)
    session.command("scp.empty", name="Before gesture")
    before = session.document
    session.begin()
    session.replace_document(name="Uncommitted drag")
    provisional, cursor = session.document, session.history.cursor
    advance(session, saver, now)
    recovered, _ = read_package(Path(saver.last["path"]), session.engine)
    assert recovered == before and session.document is provisional
    assert session.history.before is before and session.history.cursor == cursor
    session.cancel()
    assert session.document.name == before.name


def test_autosave_uses_checkpoint_while_writers_are_pending(session, tmp_path):
    saver, now = service(session, tmp_path)
    session.command("scp.empty", name="Accepted")
    before = session.document
    release = pending_write(session)
    session.replace_document(name="Still calculating")
    now[0] += 301
    saver.poll(session)
    wait_for_dispatch(session, saver)
    release.set()
    session.wait(5)
    recovered, _ = read_package(Path(saver.last["path"]), session.engine)
    assert recovered == before


def pending_write(session):
    release, started = Event(), Event()

    def execute(document, cancel):
        started.set()
        release.wait(5)

    job = Job("Slow", frozenset(("@test",)), lambda d: d, execute, lambda r: None)
    session.scheduler.submit(job)
    session.scheduler.tick()
    assert started.wait(2)
    return release


def wait_for_dispatch(session, saver):
    deadline = monotonic() + 2
    while saver.job is not None and not saver.job.started and monotonic() < deadline:
        session.scheduler.tick()
        sleep(0.002)
    assert saver.job is None or saver.job.started


def test_autosave_never_replaces_manual_project_or_changes_lock(session, tmp_path):
    original = tmp_path / "manual.anthroforge"
    session.command("save", path=str(original), blocked_policy="wait")
    before, lock = original.read_bytes(), session.file_lock
    saver, now = service(session, tmp_path)
    session.command("scp.empty", name="New anatomy")
    advance(session, saver, now)
    assert original.read_bytes() == before and session.file_lock is lock
    assert session.path == original and saver.last["origin"] == str(original)
    assert session.saved_revision < session.document.revision


def test_disabled_and_interval_settings_do_not_touch_document(session, tmp_path):
    saver, now = service(session, tmp_path)
    session.command("scp.empty", name="Edited")
    session.command("preferences.set", autosave_enabled=False)
    advance(session, saver, now)
    assert not saver.store.scan()[0]
    session.command("preferences.set", autosave_enabled=True, autosave_minutes=10)
    saver.poll(session)
    advance(session, saver, now)
    assert not saver.store.scan()[0]
    advance(session, saver, now)
    assert len(saver.store.scan()[0]) == 1


def test_retention_keeps_three_copies_and_unrelated_files(session, tmp_path):
    saver, now = service(session, tmp_path)
    saver.store.directory.mkdir()
    unrelated = saver.store.directory / "my-project.anthroforge"
    unrelated.write_bytes(b"User file")
    root = session.command("scp.empty", name="Initial")
    for index in range(KEEP + 2):
        session.command("scp.rename", entity=root, name=str(index))
        advance(session, saver, now)
    rows, _ = saver.store.scan()
    assert len(rows) == KEEP and rows[0]["revision"] == session.document.revision
    assert unrelated.read_bytes() == b"User file"
    assert not list(saver.store.directory.glob("*.lock"))


def test_failure_retries_later_and_does_not_affect_edits(session, tmp_path, monkeypatch):
    saver, now = service(session, tmp_path)
    session.command("scp.empty", name="Edited")
    write = saver.store.write
    monkeypatch.setattr(saver.store, "write", lambda *args: (_ for _ in ()).throw(OSError("disk")))
    advance(session, saver, now)
    assert saver.error == "disk" and not saver.store.scan()[0]
    monkeypatch.setattr(saver.store, "write", write)
    saver.poll(session)
    assert saver.job is None
    advance(session, saver, now)
    assert saver.last and not saver.error


def test_cancelled_serialization_retains_existing_file(session, tmp_path):
    path = tmp_path / "original.anthroforge"
    atomic_save(path, session.document, session.resources)
    original = path.read_bytes()
    canceled = Event()
    canceled.set()
    with pytest.raises(ValueError, match="cancelled"):
        atomic_save(path, session.document, session.resources, canceled)
    assert path.read_bytes() == original and not list(tmp_path.glob("*.tmp"))


@pytest.mark.parametrize("minutes", [0, -1, 1.5, True, 1441])
def test_interval_validation(session, minutes):
    with pytest.raises(ValueError, match="whole number"):
        session.command("preferences.set", autosave_minutes=minutes)


def hold_reader(session, key):
    started, release = Event(), Event()

    def execute(document, cancel):
        started.set()
        release.wait(5)

    job = Job("Reader", frozenset((key,)), lambda d: d, execute, lambda r: None, writes=False)
    session.scheduler.submit(job)
    session.scheduler.tick()
    assert started.wait(2)
    return release


def test_queued_autosave_captures_at_dispatch_and_never_overlaps(session, tmp_path):
    saver, now = service(session, tmp_path)
    root = session.command("scp.empty", name="Earlier")
    releases = [hold_reader(session, key) for key in ("@a", "@b")]
    now[0] += 301
    saver.poll(session)
    job = saver.job
    session.command("scp.rename", entity=root, name="Newest at dispatch")
    now[0] += 301
    saver.poll(session)
    assert saver.job is job and not job.started
    for release in releases:
        release.set()
    session.wait(5)
    assert read_package(Path(saver.last["path"]), session.engine)[0] == session.document


def test_project_replacement_cancels_pending_recovery_and_resets_clock(session, tmp_path):
    saver, now = service(session, tmp_path)
    session.command("scp.empty", name="Old project")
    releases = [hold_reader(session, key) for key in ("@a", "@b")]
    now[0] += 301
    saver.poll(session)
    session.scheduler.cancel_job(saver.job.id)
    for release in releases:
        release.set()
    session.wait(5)
    saver.reset()
    saver.poll(session)
    assert saver.job is None and not saver.last and saver.due > now[0]
    assert not saver.store.scan()[0]
