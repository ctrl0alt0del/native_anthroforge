"""New lifecycle and legacy image export in a relocated packaged executable."""

import json

from tissue_authoring_portable import command
from vcp_visual_portable import archive, execute, export, stroke


def painting(executable, cwd, invoke):
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "tissues.anthroforge"))
    target = next(row["state"]["id"] for row in state["objects"] if row["kind"] == "tissue")
    rows = execute(executable, cwd, invoke, "shared-paint", requests(target), "tissues.anthroforge")
    by_id = {row["id"]: row["result"] for row in rows if row.get("id")}
    assert by_id["state"]["state"] == "committed", by_id
    assert by_id["values"]["total"] > 0
    assert archive(cwd, "shared-paint-preview")["tissue"]["paint"]["authored"] is False


def requests(target):
    options = dict(stroke(target), consumer="tissue_weights", name="shared-paint")
    samples = options.pop("samples")
    return [
        command("tissue.field.create", target=target, name="shared-paint", domain="REST"),
        command("wait"),
        dict(id="stroke", **command("painting.begin", **options)),
        command("painting.append", token="$stroke.token", samples=samples),
        command("painting.finish", token="$stroke.token"),
        command("wait"),
        dict(id="state", **command("painting.status", token="$stroke.token")),
        *prepared(target, options, samples),
    ]


def prepared(target, options, samples):
    return [
        dict(id="preview", **command("painting.preview", **options, samples=samples)),
        command("wait"),
        dict(id="values", **command("painting.result", token="$preview.token")),
        export("shared-paint-preview", target, dict(stage="rest", mode="Overlay")),
        command("painting.cancel", token="$preview.token"),
        command("undo"),
        command("wait"),
    ]
