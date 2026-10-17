"""Portable executable report qualification with the caller's isolated environment."""

import json
from zipfile import ZipFile

from anthroforge import __version__


def validate(path, desktop):
    with ZipFile(path) as archive:
        data = {name: json.loads(archive.read(name)) for name in archive.namelist()}
    assert set(data) == {"manifest.json", "summary.json", "trace.json"}
    manifest, summary = data["manifest.json"], data["summary.json"]
    assert manifest["schema_version"] == 1 and manifest["complete"], manifest
    assert manifest["environment"]["build"]["packaged"]
    assert manifest["environment"]["application_version"] == __version__
    verify_capabilities(manifest, desktop)
    verify_durations(summary, desktop)
    verify_events(data["trace.json"]["traceEvents"])
    return manifest


def verify_capabilities(manifest, desktop):
    assert manifest["capabilities"]["qml"] == desktop
    if desktop:
        expected = {"CanvasFrameRate", "EngineControl", "DebugMessages"}
        assert set(manifest["qt"]["services"]) == expected


def verify_durations(summary, desktop):
    keys = summary["durations"]
    assert (
        any("Activity.qml" in k for k in keys)
        if desktop
        else any(k.startswith("native/") for k in keys)
    )


def verify_events(events):
    assert all(e["ph"] in ("X", "i") and isinstance(e["tid"], int) for e in events)


def profiling(executable, cwd, invoke):
    headless = capture_headless(executable, cwd, invoke)
    arguments = ("--project", "assembly.anthroforge", "--profile-probe", str(cwd / "probe.json"))
    invoke(executable, cwd, *arguments)
    state = json.loads((cwd / "probe.json").read_text())
    assert state["state"] == "saved", state
    desktop = validate(cwd / "probe.afprofile.zip", True)
    (cwd / "profiling-check.json").write_text(json.dumps(dict(headless=headless, desktop=desktop)))


def capture_headless(executable, cwd, invoke):
    requests = [
        dict(operation="profile.start", arguments={}),
        dict(operation="primitive.create", arguments=dict(kind="BODY")),
        dict(operation="wait", arguments={}),
        dict(operation="profile.stop", arguments=dict(path="headless.afprofile.zip", wait=True)),
    ]
    (cwd / "profile.json").write_text(json.dumps(requests))
    invoke(executable, cwd, "--cli", "run", "profile.json")
    return validate(cwd / "headless.afprofile.zip", False)
