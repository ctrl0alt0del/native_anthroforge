"""Qualify tissue inspection and frozen colored views in the shipped executable."""

import json
from zipfile import ZipFile

from tissue_authoring_portable import command


def qualify(executable, cwd, invoke, target):
    batch = cwd / "tissue-inspection.json"
    batch.write_text(json.dumps(requests(target)), encoding="utf-8")
    output = invoke(executable, cwd, "--cli", "run", batch.name, "--project", "tissues.anthroforge")
    rows = [json.loads(line) for line in output.splitlines()]
    assert all(row["ok"] for row in rows), rows
    with ZipFile(cwd / "tissue-stages.afinspection.zip") as archive:
        data = json.loads(archive.read("inspection.json"))
        assert archive.read("image.png").startswith(b"\x89PNG")
    assert data["view"]["tissue"]["mode"] == "Displacement"
    assert data["view"]["tissue"]["point"]["asset"]
    assert not data["image"]["window_visible"]


def requests(target):
    point = dict(target=target, stage="rest", triangle=0, weights=[0.2, 0.3, 0.5])
    return [
        command("tissue.inspect.compare", target=target, stage="rest", reference="base"),
        command("tissue.inspect.point", **point),
        command("tissue.inspect.check", target=target, stage="rest"),
        command("wait"),
        command("tissue.inspect.status", kind="comparison"),
        command("tissue.inspect.status", kind="point"),
        export(target),
        command("tissue.inspect.cancel"),
    ]


def export(target):
    view = dict(stage="rest", reference="base", mode="Displacement")
    return command(
        "inspection.export",
        path="tissue-stages.afinspection.zip",
        selected=target,
        tissue=view,
        wait=True,
    )
