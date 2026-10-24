"""Frozen comparison archives replay only whitelisted semantics in isolated sessions."""

import json
from zipfile import ZipFile

import pytest

from anthroforge.application import comparison_archive, comparison_replay
from tests.test_inspection_export import fake_render
from tests.test_shortcut_comparison import baseline


def exported(session, tmp_path, monkeypatch, replay=True):
    monkeypatch.setattr(comparison_archive, "render", fake_render)
    target, key = baseline(session)
    session.command("driver.value", driver=key, value=16)
    session.wait(10)
    path = tmp_path / "comparison.afinspection.zip"
    session.command("inspection.export", path=str(path), replay=replay, wait=True)
    return path, target, key


def test_export_and_replay_are_isolated(session, tmp_path, monkeypatch):
    path, target, _ = exported(session, tmp_path, monkeypatch)
    original = session.document
    result = session.command("inspection.replay", path=str(path))
    assert session.document is original
    row = next(r for r in result["comparison"]["rows"] if r["id"] == target)
    assert "geometry" in row["changes"]
    with ZipFile(path) as archive:
        data = json.loads(archive.read("inspection.json"))
    expected = next(r for r in data["comparison"]["differences"]["rows"] if r["id"] == target)
    for stage in ("before", "after"):
        assert row[stage]["geometry"] == expected[stage]["geometry"]
        assert row[stage]["frame"] == expected[stage]["frame"]


def test_replay_is_explicit_opt_in(session, tmp_path, monkeypatch):
    path, _, _ = exported(session, tmp_path, monkeypatch, replay=False)
    with ZipFile(path) as archive:
        assert "starting.anthroforge" not in archive.namelist()
    with pytest.raises(ValueError, match="does not contain replay"):
        session.command("inspection.replay", path=str(path))


def test_whitelist_rejects_external_operations():
    from anthroforge import __version__

    data = dict(
        schema_version=1,
        application_version=__version__,
        complete=True,
        operations=[dict(operation="open", arguments=dict(path="external"))],
    )
    with pytest.raises(ValueError, match="Unsupported replay operation"):
        comparison_replay.validate_journal(data)


def test_export_freezes_baseline_across_clear(session, tmp_path, monkeypatch):
    monkeypatch.setattr(comparison_archive, "render", fake_render)
    baseline(session)
    path = tmp_path / "comparison.afinspection.zip"
    session.command("inspection.export", path=str(path), replay=True)
    session.command("shortcut.comparison.clear")
    session.wait(10)
    with ZipFile(path) as archive:
        assert "starting.anthroforge" in archive.namelist()
