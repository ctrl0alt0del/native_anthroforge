"""Automatic source conversion through the packaged, Qt-free command catalogue."""

import json

from construction_portable import request


def automatic_construction(executable, cwd, invoke):
    script = cwd / "automatic-construction.json"
    script.write_text(json.dumps(commands()), encoding="utf-8")
    output = invoke(executable, cwd, "--cli", "run", script.name)
    replies = [json.loads(line) for line in output.splitlines()]
    assert all(row["ok"] for row in replies), replies
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "automatic.anthroforge"))
    verify(state)
    converted_surfaces(executable, cwd, invoke, state)


def commands():
    return [
        dict(id="bone", **request("import", path="examples/primitives/cube.obj", units=1)),
        request("wait"),
        *curves(),
        request("surface.create", curves=["$first", "$second"]),
        request("wait"),
        dict(id="point", **request("construction.point.create", position=[0, 0, 0.8])),
        request("tissue.create", source="$point", preset="CLOSED_BULK"),
        request("wait"),
        request("save", path="automatic.anthroforge", blocked_policy="wait"),
    ]


def curves():
    return [
        dict(id="first", **request("curve.create", name="First", points=points(-0.2))),
        dict(id="second", **request("curve.create", name="Second", points=points(0.2))),
        request("wait"),
        request("tissue.create", source="$first", preset="RIM"),
        request("wait"),
    ]


def points(y):
    return [dict(position=[x, y, z]) for x, z in [(-0.4, 0.7), (0, 0.8), (0.4, 0.7)]]


def verify(state):
    rows = [row["state"] for row in state["objects"]]
    tissues = [row for row in rows if "source" in row and "parts" in row]
    assert len(tissues) == 2
    lookup = {row["id"]: row for row in rows}
    for tissue in tissues:
        assert tissue["result"]["status"] == "ready" and tissue["result"]["asset"]
        source = lookup[tissue["source"]]
        assert source.get("bindings") or source.get("binding")
    assert not state["save_blocked"]


def converted_surfaces(executable, cwd, invoke, state):
    source = next(row["state"]["id"] for row in state["objects"] if row["kind"] == "surface")
    script = cwd / "automatic-surfaces.json"
    script.write_text(json.dumps(surface_commands(source)), encoding="utf-8")
    output = invoke(
        executable, cwd, "--cli", "run", script.name, "--project", "automatic.anthroforge"
    )
    assert all(json.loads(line)["ok"] for line in output.splitlines())
    saved = json.loads(
        invoke(executable, cwd, "--cli", "inspect", "automatic-surfaces.anthroforge")
    )
    verify_surfaces(saved)


def surface_commands(source):
    return [
        request("membrane.create", source=source),
        request("tissue.create", source=source),
        request("wait"),
        request("save", path="automatic-surfaces.anthroforge", blocked_policy="wait"),
    ]


def verify_surfaces(state):
    rows = state["objects"]
    lookup = {row["state"]["id"]: row for row in rows}
    membranes = [row["state"] for row in rows if row["kind"] == "membrane"]
    assert len(membranes) == 2
    for membrane in membranes:
        assert membrane["result"]["status"] == "ready"
        assert all(lookup[use["curve"]]["kind"] == "fiber" for use in membrane["curves"])
    assert sum(row["kind"] == "tissue" for row in rows) == 3
    assert all(row["state"]["result"]["status"] == "ready" for row in rows)
    assert not state["save_blocked"]
