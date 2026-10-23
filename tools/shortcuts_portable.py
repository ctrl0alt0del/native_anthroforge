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
    body = dict(id="body", **request("primitive.from_curves", curves=["$circle"], kind="BODY"))
    inspect = dict(id="body_spec", **request("primitive.inspect", entity="$body"))
    dimensions = dict(
        entity="$body", piece="$body_spec.primitive.pieces.0.id", width=0.01, depth=0.01
    )
    return [
        body,
        inspect,
        request("body.update", **dimensions),
        request("wait"),
        request("save", path="shortcuts.anthroforge", blocked_policy="wait"),
    ]


def request(operation, **arguments):
    return dict(operation=operation, arguments=arguments)


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


def inspection_view(state):
    return dict(
        camera=[0, 0, 0, 70, 0, 0, 0.25],
        orthographic=True,
        workspace=0,
        selected=state["entities"][0]["id"],
        editing=False,
    )


def render(executable, cwd, invoke, state):
    (cwd / "shortcuts-view.json").write_text(json.dumps(inspection_view(state)))
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
