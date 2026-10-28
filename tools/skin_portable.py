"""Exercise skin workers, fitting, persisted playback and OBJ in a relocated package."""

import json
from zipfile import ZipFile

import numpy as np


def qualify(executable, cwd, invoke):
    output = invoke(executable, cwd, "--cli", "run", "examples/skin.json")
    assert all(json.loads(line)["ok"] for line in output.splitlines())
    inspect = invoke(executable, cwd, "--cli", "inspect", "skin.anthroforge")
    state = json.loads(inspect)
    assert state["skin_available"] and not state["save_blocked"]
    verify_saved(cwd)
    audit(executable, cwd, invoke)
    preview(executable, cwd, invoke)


def audit(executable, cwd, invoke):
    operations = [dict(operation="skin.report"), dict(operation="skin.envelope.reset")]
    path = cwd / "skin-audit.json"
    path.write_text(json.dumps(operations), encoding="utf-8")
    text = invoke(executable, cwd, "--cli", "run", str(path), "--project", "skin.anthroforge")
    rows = [json.loads(line) for line in text.splitlines()]
    assert all(row["ok"] for row in rows)
    report = rows[0]["result"]
    assert "solver" in report["final"]["report"]
    assert "intersections" in report["final"]["report"]
    assert "budgets" in report["topology"]["report"]


def verify_saved(cwd):
    with ZipFile(cwd / "skin.anthroforge") as archive:
        document = json.loads(archive.read("manifest.json"))["document"]
    skin = document["skin"]
    assert skin["reference"] and skin["final"]["status"] == "ready"
    assert len(skin["fits"]) == 1
    rows = [r.split() for r in (cwd / "skin.obj").read_text().splitlines()]
    faces = [r for r in rows if r[0] == "f"]
    vertices = np.array([[float(v) for v in r[1:]] for r in rows if r[0] == "v"])
    assert len(faces) > 100 and all(len(r) == 5 for r in faces)
    assert vertices.shape[1] == 3 and np.isfinite(vertices).all()


def preview(executable, cwd, invoke):
    operations = [
        dict(id="skin", operation="skin.inspect"),
        dict(operation="skin.fit.preview", arguments=dict(identity="$skin.fits.0.id", value=0.15)),
        dict(operation="wait"),
        dict(id="preview", operation="skin.fit.preview.status"),
        dict(operation="skin.fit.preview.cancel"),
    ]
    path = cwd / "skin-preview.json"
    path.write_text(json.dumps(operations), encoding="utf-8")
    text = invoke(executable, cwd, "--cli", "run", str(path), "--project", "skin.anthroforge")
    rows = [json.loads(line) for line in text.splitlines()]
    assert all(row["ok"] for row in rows)
    assert next(row["result"]["visible"] for row in rows if row["id"] == "preview")
