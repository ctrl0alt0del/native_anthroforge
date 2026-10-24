"""Diagnostics do not corrupt user edits, report archives, or later replay inputs."""

import json
from dataclasses import replace
from pathlib import Path
from threading import Event
from zipfile import ZipFile

import pytest

from anthroforge.application import comparison_archive, comparison_replay
from anthroforge.application.comparison_capture import capture
from anthroforge.application.comparison_journal import Journal
from anthroforge.feedback.attachments import materialize
from anthroforge.feedback.local_inbox import LocalReportInbox
from anthroforge.feedback.storage import LocalReportConsumer
from tests.test_comparison_archive import exported
from tests.test_feedback import example
from tests.test_shortcut_comparison import baseline


def test_journal_serialization_failure_does_not_fail_the_edit():
    journal = Journal()
    journal.append("driver.value", dict(value=object()))
    assert journal.stopped and not journal.describe()["complete"]


def test_capture_journal_is_owned_and_preference_changes_are_reported(session):
    _, key = baseline(session)
    frozen = capture(session, True)
    session.command("driver.value", driver=key, value=12)
    assert frozen.journal["operations"] == []
    session.preferences.update(routing_backend="PIQP")
    assert not capture(session, True).journal["complete"]


def test_archive_rejects_unsafe_names_before_extraction(tmp_path):
    path = tmp_path / "bad.zip"
    with ZipFile(path, "w") as archive:
        archive.writestr("../outside", "no")
    with pytest.raises(ValueError, match="Unexpected"):
        comparison_replay.unpack(path, tmp_path, Event())


def test_checksum_mismatch_cannot_dispatch(session, tmp_path, monkeypatch):
    path, _, _ = exported(session, tmp_path, monkeypatch)
    with ZipFile(path) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    files["replay.json"] = b"{}"
    with ZipFile(path, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    with pytest.raises(ValueError, match="checksum mismatch"):
        session.command("inspection.replay", path=str(path))


def test_streamed_attachment_survives_text_edit_and_is_deleted_with_report(tmp_path):
    attachment = materialize("comparison.afinspection.zip", lambda p: p.write_bytes(b"evidence"))
    report = replace(example(), files=(attachment,))
    receipt = LocalReportConsumer(tmp_path).submit(report)
    inbox, key = LocalReportInbox(tmp_path), Path(receipt.location).name
    inbox.update_description(key, "Updated text")
    with ZipFile(receipt.location) as archive:
        assert archive.read(attachment.name) == b"evidence"
        assert (
            json.loads(archive.read("report.json"))["attachments"][attachment.name]
            == attachment.checksum
        )
    inbox.delete(key)
    assert not Path(receipt.location).exists()


def test_failed_export_retains_baseline_and_existing_file(session, tmp_path, monkeypatch):
    baseline(session)
    original = session.shortcut_comparison.baseline
    path = tmp_path / "failure.afinspection.zip"
    path.write_bytes(b"previous")
    monkeypatch.setattr(comparison_archive, "render", fail_render)
    with pytest.raises(ValueError, match="renderer failed"):
        session.command("inspection.export", path=str(path), wait=True)
    assert path.read_bytes() == b"previous" and session.shortcut_comparison.baseline is original


def fail_render(*args):
    raise ValueError("renderer failed")
