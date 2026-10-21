"""Exercise native visual tools and frozen replay in the relocated executable."""

import json
from zipfile import ZipFile

from tissue_authoring_portable import command

VIEW = [0, 0, 4, 1, 0, 0, 0, 1, 0, 0, 0, -1, 300, 1]


def execute(executable, cwd, invoke, name, commands, project):
    batch = cwd / (name + ".json")
    batch.write_text(json.dumps(commands), encoding="utf-8")
    output = invoke(executable, cwd, "--cli", "run", batch.name, "--project", project)
    rows = [json.loads(line) for line in output.splitlines()]
    assert all(row["ok"] for row in rows), rows
    return rows


def archive(cwd, name):
    with ZipFile(cwd / (name + ".afinspection.zip")) as report:
        assert report.read("image.png").startswith(b"\x89PNG")
        value = json.loads(report.read("inspection.json"))
    assert not value["image"]["window_visible"]
    return value["view"]


def qualify(executable, cwd, invoke, items):
    first, second = items["Layer 1"]["id"], items["Layer 2"]["id"]
    execute(executable, cwd, invoke, "visual-paint", painting(first), "tissues.anthroforge")
    assert archive(cwd, "visual-paint")["tissue"]["paint"]["authored"] is False
    commands = stacking(first, second) + sections(second)
    execute(executable, cwd, invoke, "visual-sections", commands, "tissues.anthroforge")
    assert archive(cwd, "visual-stacking")["tissue"]["stacking"]["report"]["lines"]
    assert archive(cwd, "visual-section")["tissue"]["section"]["report"]["surfaces"]


def painting(target):
    return [
        command("tissue.field.create", target=target, name="paint", domain="REST"),
        command("wait"),
        dict(id="paint", **command("tissue.inspect.paint", **stroke(target))),
        command("wait"),
        export("visual-paint", target, dict(stage="rest", mode="Overlay")),
        command("tissue.field.paint.commit", job="$paint.job"),
        command("wait"),
        command("undo"),
        command("wait"),
    ]


def stroke(target):
    return dict(
        target=target,
        name="paint",
        stage="rest",
        view=VIEW,
        samples=[[0, 0], [20, 10]],
        brush=[1000, 1, 1, 1, False],
    )


def stacking(first, second):
    return [
        command("tissue.inspect.stacking", target=second, other=first),
        command("wait"),
        export("visual-stacking", second, dict(stage="intrinsic", mode="Overlay")),
    ]


def sections(target):
    section = dict(
        enabled=True, target=target, axis=0, position=0, flip=False, cut=True, wholeScene=False
    )
    return [
        command("tissue.inspect.section", target=target, stage="rest", plane=[1, 0, 0, 0]),
        command("wait"),
        export("visual-section", target, dict(stage="rest", mode="Overlay", section=section)),
    ]


def export(name, target, tissue):
    return command(
        "inspection.export",
        path=name + ".afinspection.zip",
        selected=target,
        tissue=tissue,
        wait=True,
    )


def route(executable, cwd, invoke, backend):
    project = backend + ".anthroforge"
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", project))
    target = next(row["state"]["id"] for row in state["objects"] if row["kind"] == "fiber")
    name = "visual-route-" + backend
    execute(executable, cwd, invoke, name, route_commands(target, name), project)
    report = archive(cwd, name)["route"]["report"]
    assert report["success"] and report["backend"] == backend and report["records"]


def route_commands(target, name):
    return [
        command("curve.inspect.route", target=target, cold=True),
        command("wait"),
        command(
            "inspection.export",
            path=name + ".afinspection.zip",
            selected=target,
            route=dict(index=0, showContacts=True),
            wait=True,
        ),
    ]
