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
        request("preferences.set", routing_backend=backend, fiber_propagation=propagation(backend)),
        request("profile.start"),
        request("import", path="examples/primitives/cube.obj", units=1),
        request("wait"),
        dict(id="curve", **request("curve.create", engine="ROUTED", points=points)),
        request("wait"),
        request("fiber.create", curve="$curve"),
        *finish_evaluation(backend),
    ]


def propagation(backend):
    return "LOCAL_SURFACE" if backend == "CUSTOM" else "SMOOTH_SHAPE"


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
    assert rows[0]["result"]["fiber_propagation"] == "SMOOTH_SHAPE"
    desktop_preferences(executable, cwd, invoke)
    conversion(executable, cwd, invoke)
    reset = [
        request("preferences.set", routing_backend="CUSTOM", routing_conversion_points="ENDPOINTS")
    ]
    execute(executable, cwd, invoke, "preferences-reset", reset)


def conversion(executable, cwd, invoke):
    for mode, count in (("ENDPOINTS", 2), ("ALL_POINTS", 3)):
        execute(executable, cwd, invoke, "conversion-" + mode, conversion_commands(mode))
        with ZipFile(cwd / ("conversion-" + mode + ".anthroforge")) as archive:
            state = json.loads(archive.read("manifest.json"))["document"]["objects"][0]["state"]
        assert len(state["points"]) == count and state["engine_settings"]["kind"] == "ROUTED"
        assert state["result"]["status"] == "ready", state["result"]


def conversion_commands(mode):
    points = [dict(position=p) for p in ((-1, 0, 0), (0, 1, 0), (1, 0, 0))]
    return [
        request("preferences.set", routing_conversion_points=mode),
        dict(id="source", **request("curve.create", points=points)),
        request("wait"),
        request("curve.engine", curve="$source", engine="ROUTED"),
        request("wait"),
        request("save", path="conversion-" + mode + ".anthroforge", blocked_policy="wait"),
    ]


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
    verify_desktop(json.loads(result), executable)


def verify_desktop(result, executable):
    assert result["desktop_smoke"]
    state = result["preferences"]
    assert state["executable"] == str(executable) and state["enabled"], state
    assert state["tooltip"] == "applicationToolTip" and state["visible"], state
    assert state["width"] <= 380 and state["lines"] > 1, state
    commands = [v for key, _, v in state["registration"] if key.endswith(r"shell\open\command")]
    assert commands == [f'"{executable}" --project "%1"'] * 2


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
    assert all(e["args"]["fiber_propagation"] == propagation(backend) for e in calls)
