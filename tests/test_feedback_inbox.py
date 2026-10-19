"""Existing report format, independent inbox capability and deletion isolation."""

import json
from dataclasses import replace
from uuid import uuid4
from zipfile import BadZipFile, ZipFile

import pytest

from anthroforge.feedback.local_inbox import LocalReportInbox
from anthroforge.feedback.storage import LocalReportConsumer
from tests.test_feedback import example


def test_existing_reports_preview_delete_and_missing_inbox(tmp_path):
    inbox = LocalReportInbox(tmp_path / "inbox")
    assert inbox.entries() == () and not inbox.directory.exists()
    consumer, original = LocalReportConsumer(inbox.directory), example()
    consumer.submit(original)
    consumer.submit(replace(original, id=uuid4().hex, created_at="2026-10-20", description="Newer"))
    entries = inbox.entries()
    assert len(entries) == 2 and entries[0].title == "Newer"
    assert_preview(inbox, entries[1].key, original)
    inbox.delete(entries[1].key)
    inbox.delete(entries[1].key)
    assert inbox.entries() == (entries[0],)
    assert inbox.read(entries[0].key).description == "Newer"


def assert_preview(inbox, key, original):
    detail = inbox.read(key)
    assert detail.description == original.description
    assert detail.annotated_png == original.annotated_png


@pytest.mark.parametrize("key", ["../outside.afreport.zip", "nested/a.afreport.zip", "other.txt"])
def test_report_keys_cannot_escape_inbox(tmp_path, key):
    outside = tmp_path / "outside.afreport.zip"
    outside.write_bytes(b"preserve")
    inbox = LocalReportInbox(tmp_path / "inbox")
    with pytest.raises(ValueError, match="Select a report"):
        inbox.delete(key)
    with pytest.raises(ValueError, match="Select a report"):
        inbox.read(key)
    assert outside.read_bytes() == b"preserve"


def test_corrupt_and_future_reports_do_not_hide_valid_reports(tmp_path):
    consumer, inbox = LocalReportConsumer(tmp_path), LocalReportInbox(tmp_path)
    consumer.submit(example())
    (tmp_path / "corrupt.afreport.zip").write_bytes(b"bad archive")
    with ZipFile(tmp_path / "future.afreport.zip", "w") as output:
        output.writestr("report.json", json.dumps(dict(schema_version=100)))
    entries = inbox.entries()
    assert len(entries) == 3 and sum(bool(row.error) for row in entries) == 2
    for row in entries:
        if row.error:
            with pytest.raises((ValueError, BadZipFile)):
                inbox.read(row.key)
            inbox.delete(row.key)
    assert len(inbox.entries()) == 1


def test_oversized_report_metadata_is_bounded(tmp_path):
    with ZipFile(tmp_path / "large.afreport.zip", "w") as output:
        output.writestr("report.json", b"x" * (2 * 1024 * 1024 + 1))
    inbox = LocalReportInbox(tmp_path)
    assert "size limit" in inbox.entries()[0].error
    with pytest.raises(ValueError, match="size limit"):
        inbox.read("large.afreport.zip")


def test_delete_failure_preserves_report_and_other_files(tmp_path, monkeypatch):
    from pathlib import Path

    consumer, inbox = LocalReportConsumer(tmp_path), LocalReportInbox(tmp_path)
    consumer.submit(example())
    entry = inbox.entries()[0]
    with monkeypatch.context() as patch:
        patch.setattr(
            Path, "unlink", lambda *args, **kw: (_ for _ in ()).throw(PermissionError("locked"))
        )
        with pytest.raises(PermissionError, match="locked"):
            inbox.delete(entry.key)
    assert inbox.entries() == (entry,)


def archive_members(path):
    with ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def test_description_edit_preserves_identity_images_and_metadata(tmp_path):
    inbox = LocalReportInbox(tmp_path)
    original = example()
    path = LocalReportConsumer(tmp_path).submit(original).location
    before = archive_members(path)
    key = inbox.entries()[0].key
    inbox.update_description(key, " Updated Україна\nSecond line ")
    after = archive_members(path)
    assert after["description.txt"].decode() == "Updated Україна\nSecond line"
    assert all(after[name] == before[name] for name in ("original.png", "annotated.png"))
    metadata = json.loads(after["report.json"])
    assert metadata.pop("updated_at")
    metadata["description"] = original.description
    assert metadata == json.loads(before["report.json"])
    assert inbox.read(key).description == "Updated Україна\nSecond line"


def test_description_edit_failure_preserves_archive_and_cleans_temporary_file(
    tmp_path, monkeypatch
):
    from anthroforge.feedback import report_editing

    path = LocalReportConsumer(tmp_path).submit(example()).location
    inbox, before = LocalReportInbox(tmp_path), archive_members(path)
    key = inbox.entries()[0].key
    monkeypatch.setattr(
        report_editing.os, "replace", lambda *args: (_ for _ in ()).throw(OSError("full"))
    )
    with pytest.raises(OSError, match="full"):
        inbox.update_description(key, "Changed")
    assert archive_members(path) == before and len(list(tmp_path.iterdir())) == 1


def test_empty_description_is_rejected_without_mutating_report(tmp_path):
    path = LocalReportConsumer(tmp_path).submit(example()).location
    inbox, before = LocalReportInbox(tmp_path), archive_members(path)
    with pytest.raises(ValueError, match="Add a description"):
        inbox.update_description(inbox.entries()[0].key, " \n ")
    assert archive_members(path) == before
