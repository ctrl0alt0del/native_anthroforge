"""A portable app owns its worker and never falls back to a developer checkout."""

import json
import os
from pathlib import Path

import pytest

from anthroforge.application import skin_avbd
from anthroforge.application import skin_avbd_identity as identity
from anthroforge.application import skin_avbd_runtime as runtime


def package(tmp_path, monkeypatch):
    target = tmp_path / "anthroforge/_runtime"
    target.mkdir(parents=True)
    (target / "build.json").write_text('{"packaged": true}')
    monkeypatch.setattr(runtime, "PACKAGE", target)
    root = target / "avbd"
    for relative in (runtime.WORKER, Path("python/python.exe")):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    (root / "manifest.json").write_text(json.dumps(dict(schema=1, required=[])))
    return root


def test_packaged_runtime_ignores_external_override(tmp_path, monkeypatch):
    root = package(tmp_path, monkeypatch)
    monkeypatch.setenv("ANTHROFORGE_AVBD_RUNTIME", str(tmp_path / "external"))
    assert runtime.installed() == (root, root / "python/python.exe")


@pytest.mark.parametrize("missing", ("manifest.json", "python/python.exe", str(runtime.WORKER)))
def test_incomplete_package_never_uses_external_runtime(tmp_path, monkeypatch, missing):
    root = package(tmp_path, monkeypatch)
    monkeypatch.setenv("ANTHROFORGE_AVBD_RUNTIME", str(tmp_path / "external"))
    (root / missing).unlink()
    with pytest.raises(ValueError, match="Reinstall the complete app folder"):
        runtime.installed()


@pytest.mark.parametrize(
    "receipt", ({"schema": 2}, {"schema": 1, "required": ["../../build.json"]})
)
def test_invalid_bundle_receipt_rejected(tmp_path, monkeypatch, receipt):
    root = package(tmp_path, monkeypatch)
    (root / "manifest.json").write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="incomplete"):
        runtime.installed()


def test_source_run_retains_explicit_development_runtime(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, "PACKAGE", tmp_path / "src/anthroforge/_runtime")
    monkeypatch.setenv("ANTHROFORGE_AVBD_RUNTIME", str(tmp_path))
    python = tmp_path / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    python.parent.mkdir(parents=True)
    python.touch()
    worker = tmp_path / runtime.WORKER
    worker.parent.mkdir(parents=True)
    worker.touch()
    assert runtime.installed() == (tmp_path, python)


def test_bundled_checkpoint_identity_tracks_dependencies_not_location(tmp_path):
    first, second = tmp_path / "first", tmp_path / "relocated"
    first.mkdir()
    second.mkdir()
    for root in (first, second):
        (root / "manifest.json").write_text('{"files": {"solver": "digest-one"}}')
    initial = identity.runtime(first)
    assert identity.runtime(second) == initial
    (second / "manifest.json").write_text('{"files": {"solver": "new-solver-digest"}}')
    assert identity.runtime(second) != initial


def test_worker_starts_isolated_without_writing_bytecode(tmp_path, monkeypatch):
    requests = []
    monkeypatch.setattr(skin_avbd.process, "run", lambda engine, req, cancel: requests.append(req))
    monkeypatch.setattr(skin_avbd, "accepted_path", lambda output: output / "skin")
    python = tmp_path / "python/python.exe"
    result = skin_avbd.execute(None, tmp_path / "job", 0, (tmp_path, python))
    assert result == tmp_path / "job/output/skin"
    assert requests[0].arguments[:3] == (str(python), "-I", "-B")
