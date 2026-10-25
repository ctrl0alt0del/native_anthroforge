"""Qualify compiled recovery capture, recent-project history and recovery discovery."""

import json
from zipfile import ZipFile


def projects(executable, cwd, invoke):
    path = cwd / "assembly.anthroforge"
    before = path.read_bytes()
    result = invoke(
        executable,
        cwd,
        "--project",
        str(path),
        "--smoke-test",
        "--smoke-panel",
        "recovery",
        "--screenshot",
        str(cwd / "recovery.png"),
    )
    verify(json.loads(result), path, before)


def verify(data, path, before):
    state = data["projects"]
    assert data["desktop_smoke"] and state["dirty"] and state["copies"] >= 1, data
    assert state["recent"][0] == str(path) and state["path"] == str(path)
    assert path.read_bytes() == before
    with ZipFile(state["recovery"]["path"]) as archive:
        assert json.loads(archive.read("recovery.json"))["origin"] == str(path)
        assert (
            json.loads(archive.read("manifest.json"))["document"]["name"] == "Recovery smoke edit"
        )
