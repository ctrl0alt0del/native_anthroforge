"""Frozen export ownership, atomic failure and Qt-free orchestration."""

import json
import sys
import zipfile
from threading import Event

import pytest

from anthroforge.application import report_archive, report_renderer
from anthroforge.application.geometry_ownership import collect
from tests.test_construction_contracts import create


def fake_render(root, revision, cancel):
    report_archive.check(cancel)
    view = json.loads((root / "view.json").read_text())
    (root / "image.png").write_bytes(b"test image")
    data = dict(captured=True, revision=revision, inspection_view=view, scene=view)
    (root / "image.png.json").write_text(json.dumps(data))


def test_export_freezes_selection_geometry_and_units_without_undo(session, tmp_path, monkeypatch):
    monkeypatch.setattr(report_archive, "render", fake_render)
    entity = create(session)
    session.command("workspace.update", display_units="mm")
    original = session.document
    path = tmp_path / "report.afinspection.zip"
    result = session.command("inspection.export", path=str(path), selected=entity)
    session.command("scp.delete", entity=entity)
    collect(session)
    session.wait(10)
    assert result["revision"] == original.revision
    with zipfile.ZipFile(path) as archive:
        data = json.loads(archive.read("inspection.json"))
    assert data["entities"][0]["id"] == entity and data["entities"][0]["geometry"]["available"]
    assert data["view"]["selected"] == entity and data["workspace"]["display_units"] == "mm"


def test_failed_renderer_preserves_existing_report_and_allows_retry(session, tmp_path, monkeypatch):
    path = tmp_path / "report.afinspection.zip"
    path.write_bytes(b"previous report")
    monkeypatch.setattr(
        report_archive, "render", lambda *a: (_ for _ in ()).throw(ValueError("GPU"))
    )
    before = session.document
    with pytest.raises(ValueError, match="GPU"):
        session.command("inspection.export", path=str(path), wait=True)
    assert path.read_bytes() == b"previous report" and session.document is before
    monkeypatch.setattr(report_archive, "render", fake_render)
    session.command("inspection.export", path=str(path), wait=True)
    assert zipfile.is_zipfile(path)


def test_export_has_single_lifecycle_no_save_barrier_and_no_qt_import(
    session, tmp_path, monkeypatch
):
    monkeypatch.setattr(report_archive, "render", fake_render)
    path = str(tmp_path / "report.afinspection.zip")
    qt_before = {key for key in sys.modules if key.startswith("PySide6")}
    result = session.command("inspection.export", path=path)
    assert not session.scheduler.blocked
    with pytest.raises(ValueError, match="already"):
        session.command("inspection.export", path=path)
    session.command("job.cancel", job_id=result["job"])
    session.wait(5)
    assert qt_before == {key for key in sys.modules if key.startswith("PySide6")}


def test_archive_cancellation_preserves_destination(tmp_path):
    path, image = tmp_path / "report.afinspection.zip", tmp_path / "image.png"
    path.write_bytes(b"original")
    image.write_bytes(b"image")
    cancel = Event()
    cancel.set()
    with pytest.raises(ValueError, match="cancelled"):
        report_archive.archive(path, image, {}, cancel)
    assert path.read_bytes() == b"original"
    assert not list(tmp_path.glob(".afinspection-*"))


def test_renderer_command_uses_runtime_kind_instead_of_executable_name(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "executable", "renamed application.exe")
    executable = str(tmp_path / "relocated application.exe")
    monkeypatch.setattr(sys, "argv", [executable, "--cli", "report"])
    assert report_renderer.command(tmp_path, 4)[1:3] == ["-m", "anthroforge"]
    monkeypatch.setattr(report_renderer, "__compiled__", object(), raising=False)
    assert report_renderer.command(tmp_path, 4)[1:3] == ["--cli", "render"]
    assert report_renderer.command(tmp_path, 4)[0] == executable
