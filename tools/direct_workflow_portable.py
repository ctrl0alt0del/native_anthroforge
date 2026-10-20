"""New automatic binding/deletion contracts through the packaged command catalogue."""

import json

from construction_portable import request


def direct_workflows(executable, cwd, invoke):
    script = cwd / "direct-workflows.json"
    script.write_text(json.dumps(commands()), encoding="utf-8")
    output = invoke(executable, cwd, "--cli", "run", script.name)
    replies = [json.loads(line) for line in output.splitlines()]
    assert all(row["ok"] for row in replies), replies
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "direct.anthroforge"))
    verify(state)
    plan = replies[-2]["result"]
    assert plan["operation"] == "object.delete" and not plan["affected"]


def commands():
    return [
        dict(id="bone", **request("import", path="examples/primitives/cube.obj", units=1)),
        request("wait"),
        dict(id="source", **request("curve.create", name="Source")),
        request("wait"),
        request("fiber.create", curve="$source"),
        request("wait"),
        request("undo"),
        request("redo"),
        request("wait"),
        request("object.delete.inspect", target="$source"),
        request("save", path="direct.anthroforge", blocked_policy="wait"),
    ]


def verify(state):
    assert not state["save_blocked"]
    source, fiber = (row["state"] for row in state["objects"])
    assert source["name"] == "Source" and fiber["name"] == "Fiber"
    assert len(fiber["bindings"]) == 2
    assert all(b["role"] == "SCP_GEOMETRY" for b in fiber["bindings"])
    assert {p["id"] for p in source["points"]}.isdisjoint(p["id"] for p in fiber["points"])
    assert source["result"]["status"] == fiber["result"]["status"] == "ready"
