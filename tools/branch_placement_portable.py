"""Branched source/junction workflow in a relocated packaged executable."""

import json

from construction_portable import request


def branches(executable, cwd, invoke):
    output = invoke(executable, cwd, "--cli", "run", "examples/branched_curves.json")
    assert all(json.loads(line)["ok"] for line in output.splitlines()), output
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "branched.anthroforge"))
    surface = next(row["state"] for row in state["objects"] if row["kind"] == "surface")
    assert surface["kind"] == "BRANCHED" and surface["result"]["status"] == "ready"
    convert(executable, cwd, invoke, surface["id"])


def convert(executable, cwd, invoke, source):
    script = cwd / "branched-membrane.json"
    script.write_text(json.dumps(conversion_commands(source)), encoding="utf-8")
    output = invoke(
        executable, cwd, "--cli", "run", script.name, "--project", "branched.anthroforge"
    )
    assert all(json.loads(line)["ok"] for line in output.splitlines()), output
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "branched-membrane.anthroforge"))
    item = next(row["state"] for row in state["objects"] if row["kind"] == "membrane")
    assert item["kind"] == "BRANCHED" and item["result"]["status"] == "ready"


def conversion_commands(source):
    return [
        request("membrane.create", source=source),
        request("wait"),
        request("undo"),
        request("redo"),
        request("wait"),
        request("save", path="branched-membrane.anthroforge", blocked_policy="wait"),
    ]
