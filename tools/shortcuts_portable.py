"""Shortcut formulas and Parametric consumers through the packaged executable."""

import io
import json
from zipfile import ZipFile

import numpy as np


def shortcuts(executable, cwd, invoke):
    requests = json.loads((cwd / "examples/shortcuts_parametric.json").read_text())
    requests = [r for r in requests if r["operation"] != "save"]
    requests.extend(consumer_requests())
    (cwd / "shortcuts.json").write_text(json.dumps(requests))
    output = invoke(executable, cwd, "--cli", "run", "shortcuts.json")
    rows = [json.loads(row) for row in output.splitlines() if row.startswith("{")]
    assert rows and all(row["ok"] for row in rows), rows
    assert next(r for r in rows if r["id"] == "radius_result")["result"]["value"] == 0.05
    geometry(cwd / "shortcuts.anthroforge")
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "shortcuts.anthroforge"))
    render(executable, cwd, invoke, state)


def consumer_requests():
    return [
        dict(operation="primitive.from_curves", arguments=dict(curves=["$circle"], kind="BODY")),
        dict(operation="wait"),
        dict(operation="save", arguments=dict(path="shortcuts.anthroforge", blocked_policy="wait")),
    ]


def geometry(path):
    with ZipFile(path) as archive:
        state = json.loads(archive.read("manifest.json"))
        assert state["version"] == 5
        curve = state["document"]["objects"][0]["state"]
        key = curve["result"]["asset"]
        points = np.load(io.BytesIO(archive.read(f"paths/{key}/samples.npy")))
        np.testing.assert_allclose(np.linalg.norm(points[:, :2], axis=1), 0.05, atol=1e-14)
        assert len(points) == 64 and curve["engine_settings"]["kind"] == "PARAMETRIC"
        assert state["document"]["entities"][0]["result"]["asset"]


def render(executable, cwd, invoke, state):
    view = dict(camera=[0, 0, 0, 70, 0, 0, 0.25], orthographic=True, workspace=0)
    (cwd / "shortcuts-view.json").write_text(json.dumps(view))
    capture = ("--cli", "render", "shortcuts.anthroforge", "shortcuts.png")
    invoke(
        executable,
        cwd,
        *capture,
        "--revision",
        str(state["revision"]),
        "--view",
        "shortcuts-view.json",
    )
    verify_capture(cwd)


def verify_capture(cwd):
    report = json.loads((cwd / "shortcuts.png.json").read_text())
    assert report["captured"] and not report["window_visible"]
    assert report["scene"]["vertices"] > 0
