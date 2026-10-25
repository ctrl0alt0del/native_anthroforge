"""Qualify restored authoring operations through the relocated runtime, including mirrors."""

import json

import numpy as np
from construction_portable import request
from PIL import Image


def execute(executable, cwd, invoke, name, commands, project=""):
    file = cwd / (name + ".json")
    file.write_text(json.dumps(commands), encoding="utf-8")
    options = ("--project", project) if project else ()
    text = invoke(executable, cwd, "--cli", "run", file.name, *options)
    rows = [json.loads(line) for line in text.splitlines()]
    assert all(row["ok"] for row in rows), rows
    return {row["id"]: row["result"] for row in rows if row.get("id")}


def named(key, operation, **arguments):
    return dict(id=key, **request(operation, **arguments))


def inspect(executable, cwd, invoke, project):
    return json.loads(invoke(executable, cwd, "--cli", "inspect", project))


def authoring_workflows(executable, cwd, invoke):
    data = execute(executable, cwd, invoke, "authoring-build", construction())
    state = data["snapshot"]
    fiber = next(o["state"] for o in state["objects"] if o["kind"] == "fiber")
    data = execute(
        executable, cwd, invoke, "authoring-edits", edits(fiber), "authoring.anthroforge"
    )
    assert data["pins"]["records"] == [] and data["supports"]["policy"]["automatic"] is False
    assert data["appearance"]["radius"] == 0.03
    state = inspect(executable, cwd, invoke, "authoring.anthroforge")
    verify(state, fiber["id"])
    replace_and_split(executable, cwd, invoke, state)
    retarget(executable, cwd, invoke)
    render(executable, cwd, invoke, fiber["id"])


def construction():
    return [
        named("root", "scp.empty", name="Skeleton"),
        named("bone", "import", path="examples/primitives/cube.obj", units=1, parent="$root"),
        request("wait"),
        request(
            "fiber.place",
            owner="$bone.entity_id",
            points=[dict(position=[x, 0, 0.501], target="$bone.entity_id") for x in (-0.4, 0.4)],
        ),
        request("wait"),
        request("mirror.configure", target="$root", enabled=True, shift=1),
        named("snapshot", "inspect"),
        request("save", path="authoring.anthroforge", blocked_policy="wait"),
    ]


def edits(fiber):
    key, pin = fiber["id"], fiber["bindings"][0]["point"]
    commands = [
        request("fiber.supports.configure", curve=key, policy=dict(automatic=False)),
        request("fiber.binding.offset", curve=key, point=pin, value=0.02),
        request("fiber.rebind", curve=key),
        request("curve.engine_settings", curve=key, length_weight=1.1, checkpoint_steps=4),
        request("curve.reroute", curve=key),
        request("fiber.pins.check", curves=[key]),
    ]
    return settled(commands) + inspect_fiber(key)


def settled(commands):
    return [step for command in commands for step in (command, request("wait"))]


def inspect_fiber(key):
    return [
        named("pins", "issues.list", filters=dict(provider="fiber_pins.v1")),
        named("supports", "fiber.supports.inspect", curve=key),
        request("fiber.presentation", target=key, radius=0.03),
        named("appearance", "fiber.presentation.inspect", target=key),
        request("save", path="authoring.anthroforge", blocked_policy="wait"),
    ]


def verify(state, key):
    fiber = next(o["state"] for o in state["objects"] if o["state"]["id"] == key)
    assert fiber["result"]["status"] == "ready" and not fiber["support_policy"]["automatic"]
    assert fiber["engine_settings"]["checkpoint_steps"] == 4
    assert fiber["engine_settings"]["length_weight"] == 1.1


def replace_and_split(executable, cwd, invoke, state):
    target = next(e["id"] for e in state["entities"] if e["primitive"])
    commands = replacement_commands(target) + split_commands()
    result = execute(executable, cwd, invoke, "authoring-split", commands, "authoring.anthroforge")
    assert len(result["split"]["entities"]) == 2 and len(result["split"]["controls"]) == 1


def replacement_commands(target):
    commands = [
        named(
            "review", "scp.mesh.replace.assess", target=target, path="examples/primitives/cube.obj"
        ),
        request("wait"),
        named("replacement_status", "scp.mesh.replace.status"),
        request("scp.mesh.replace.apply", token="$review.token"),
        request("wait"),
        named("body", "primitive.create", kind="BODY", shape="BOX", parent=target),
        request("wait"),
        named("body_data", "primitive.inspect", entity="$body"),
    ]
    return commands


def split_commands():
    return [
        split_point(),
        request("wait"),
        named("split", "scp.split", entity="$body", points=["split-point"]),
        request("wait"),
        request("undo"),
        request("redo"),
        request("wait"),
        request("save", path="authoring-split.anthroforge", blocked_policy="wait"),
    ]


def split_point():
    return request(
        "point.insert",
        entity="$body",
        curve="$body_data.primitive.curves.0.id",
        index=1,
        point=dict(id="split-point", position=[0, 0.25, 0.15]),
    )


def retarget(executable, cwd, invoke):
    state = inspect(executable, cwd, invoke, "tissues.anthroforge")
    tissues = [o["state"] for o in state["objects"] if o["kind"] == "tissue"]
    first, second = tissues[:2]
    commands = unstacked(first, second) + retarget_commands(first, second)
    result = execute(executable, cwd, invoke, "authoring-retarget", commands, "tissues.anthroforge")
    assert len(result["sources"]) >= 2
    verify_retarget(inspect(executable, cwd, invoke, "retargeted.anthroforge"), first, second)


def unstacked(*items):
    # Coincident replacement bases intentionally cannot participate in stacking.
    return settled(
        [request("tissue.configure", target=v["id"], changes=dict(stacking=False)) for v in items]
    )


def retarget_commands(first, second):
    commands = [
        named("sources", "surface.source_ids", target=first["source"]),
        request("tissue.preset.apply", target=first["id"], preset="LAYER"),
        request("wait"),
        named(
            "review", "tissue.source.replace.assess", target=first["id"], source=second["source"]
        ),
        request("wait"),
        named("retarget_status", "tissue.source.replace.status"),
        request("tissue.source.replace.apply", token="$review.token"),
        request("wait"),
        request("save", path="retargeted.anthroforge", blocked_policy="wait"),
    ]
    return commands


def verify_retarget(state, first, second):
    tissue = next(o["state"] for o in state["objects"] if o["state"]["id"] == first["id"])
    assert tissue["source"] == second["source"] and tissue["result"]["status"] == "ready"


def render(executable, cwd, invoke, target):
    state = inspect(executable, cwd, invoke, "authoring.anthroforge")
    view = dict(workspace=0, selected=target, editing=False, orthographic=True)
    view["camera"] = [1, 0, 0.52, -90, 0, 0, 4]
    (cwd / "authoring-view.json").write_text(json.dumps(view))
    arguments = ("--cli", "render", "authoring.anthroforge", "authoring.png")
    options = ("--revision", str(state["revision"]), "--view", "authoring-view.json")
    invoke(executable, cwd, *arguments, *options)
    report = json.loads((cwd / "authoring.png.json").read_text())
    assert report["captured"] and not report["window_visible"]
    verify_fiber_pixels(cwd / "authoring.png")


def verify_fiber_pixels(path):
    pixels = np.asarray(Image.open(path).convert("RGB"))
    r, g, b = (pixels[:, :, i] for i in range(3))
    selected = (r > 200) & (g > 100) & (g < 210) & (b < 180)
    mirrored = (r > 140) & (b > 180) & (g < 180)
    assert selected.sum() > 1000 and mirrored.sum() > 1000, "Missing source/mirror Fiber tubes"
