"""Shared workflow commands plus isolated report rendering from the relocated executable."""

import json
from zipfile import ZipFile


def workflow(executable, cwd, invoke):
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "primitives.anthroforge"))
    entity = next(e["id"] for e in state["entities"] if e["primitive"])
    control = state["controls"][0]["id"]
    batch = cwd / "workflow.json"
    batch.write_text(json.dumps(requests(entity, control)), encoding="utf-8")
    output = invoke(
        executable, cwd, "--cli", "run", str(batch), "--project", "primitives.anthroforge"
    )
    rows = [json.loads(line) for line in output.splitlines() if line.startswith("{")]
    assert all(row["ok"] for row in rows), rows
    revision = rows[-1]["result"]["revision"]
    report(executable, cwd, invoke, entity, revision)


def requests(entity, control):
    return [
        dict(operation="workspace.create", arguments=dict(name="Review", members=[entity])),
        dict(operation="workspace.update", arguments=dict(display_units="mm")),
        dict(operation="workspace.preset", arguments=dict(name="shape")),
        dict(operation="inspect.target", arguments=dict(entity=control)),
        dict(operation="save", arguments=dict(path="workflow.anthroforge", blocked_policy="wait")),
    ]


def report(executable, cwd, invoke, entity, revision):
    path = cwd / "portable.afinspection.zip"
    view = ("--revision", str(revision), "--selected", entity, "--workspace", "1")
    invoke(
        executable,
        cwd,
        "--cli",
        "report",
        "workflow.anthroforge",
        str(path),
        *view,
    )
    verify_archive(path, entity, revision)


def verify_archive(path, entity, revision):
    with ZipFile(path) as archive:
        data = json.loads(archive.read("inspection.json"))
        assert archive.read("image.png").startswith(b"\x89PNG")
    assert data["revision"] == revision and data["image"]["captured"]
    assert data["view"]["selected"] == entity and data["view"]["workspace"] == 1
    assert data["workspace"]["display_units"] == "mm"
    assert data["workspace"]["unpickable_categories"] == ["geometry"]
