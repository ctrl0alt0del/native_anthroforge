"""Packaged preferences, both backend invocations, provenance and headless profiling."""

import json
from zipfile import ZipFile

from construction_portable import request
from vcp_visual_portable import route


def execute(executable, cwd, invoke, name, commands):
    script = cwd / (name + ".json")
    script.write_text(json.dumps(commands), encoding="utf-8")
    result = invoke(executable, cwd, "--cli", "run", script.name)
    rows = [json.loads(line) for line in result.splitlines()]
    assert all(row["ok"] for row in rows), rows
    return rows


def construction(backend):
    points = [dict(position=[x, 0, 0]) for x in (-0.50000001, 0.50000001)]
    return [
        request("preferences.set", routing_backend=backend),
        request("profile.start"),
        request("import", path="examples/primitives/cube.obj", units=1),
        request("wait"),
        dict(id="curve", **request("curve.create", engine="ROUTED", points=points)),
        request("wait"),
        request("fiber.create", curve="$curve"),
        *finish_evaluation(backend),
    ]


def finish_evaluation(backend):
    return [
        request("wait"),
        request("evaluate"),
        request("wait"),
        request("save", path=backend + ".anthroforge", blocked_policy="wait"),
        request("profile.stop", path=backend + ".afprofile.zip", wait=True),
    ]


def preferences(executable, cwd, invoke):
    for backend in ("CUSTOM", "PIQP"):
        execute(executable, cwd, invoke, "preferences-" + backend, construction(backend))
        verify(cwd, backend)
        route(executable, cwd, invoke, backend)
    rows = execute(executable, cwd, invoke, "preferences-reopen", [request("preferences.get")])
    assert rows[0]["result"]["routing_backend"] == "PIQP"
    desktop_preferences(executable, cwd, invoke)
    reset = [request("preferences.set", routing_backend="CUSTOM")]
    execute(executable, cwd, invoke, "preferences-reset", reset)


def desktop_preferences(executable, cwd, invoke):
    result = invoke(
        executable,
        cwd,
        "--smoke-test",
        "--smoke-panel",
        "preferences",
        "--screenshot",
        str(cwd / "preferences.png"),
    )
    assert json.loads(result)["desktop_smoke"]


def verify(cwd, backend):
    with ZipFile(cwd / (backend + ".anthroforge")) as archive:
        data = json.loads(archive.read("manifest.json"))
    paths = data["paths"]
    assert len(paths) == 2 and all(p["diagnostics"]["backend"] == backend for p in paths.values())
    objects = data["document"]["objects"]
    assert all(row["state"]["result"]["status"] == "ready" for row in objects)
    with ZipFile(cwd / (backend + ".afprofile.zip")) as archive:
        events = json.loads(archive.read("trace.json"))["traceEvents"]
    calls = [e for e in events if e["cat"] == "path" and e["name"] == "evaluate"]
    assert len(calls) >= 2 and all(e["args"]["routing_backend"] == backend for e in calls)
