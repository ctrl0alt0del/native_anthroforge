"""Repeatable automatic-routing workload; no visible UI or feature-specific markers."""

import json
import sys
from dataclasses import replace
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

from anthroforge.application.session import Session

ROOT = Path(__file__).resolve().parents[1]


def scene(session, count):
    key = session.command("import", path=str(ROOT / "examples/primitives/cube.obj"), units=1)
    session.wait(30)
    root = session.document.entity(key["entity_id"])
    copies = tuple(obstacle(session, root, i) for i in range(1, count))
    session.replace_document(entities=(root, *copies))


def obstacle(session, root, index):
    position = [2 * (index % 10), 4 + 2 * (index // 10), 0]
    matrix = session.engine.transform([*position, 0, 0, 0, 1, 1, 1])
    return replace(root, id=str(uuid4()), parent=root.id, name=f"Obstacle {index}", matrix=matrix)


def exercise(session):
    points = [dict(position=(-2, 0, 0)), dict(position=(2, 0, 0))]
    key = session.command("curve.create", engine="ROUTED", points=points)
    session.wait(30)
    for index in range(8):
        item = session.document.object(key)
        assert item.result.status == "ready", item.result.error
        session.command(
            "curve.point.update",
            curve=key,
            point=item.points[-1].id,
            position=(2, 0.02 * (index % 2), 0),
        )
        session.wait(30)
    assert session.document.object(key).result.status == "ready"


def report(path):
    with ZipFile(path) as archive:
        summary = json.loads(archive.read("summary.json"))
    return {
        key: value
        for key, value in summary["durations"].items()
        if "af_route" in key or "routing_scene" in key or "task.prepare" in key
    }


def run(directory, count=100):
    directory.mkdir(parents=True, exist_ok=True)
    session = Session("Routing scale fixture")
    try:
        scene(session, count)
        session.command("profile.start")
        exercise(session)
        path = directory / "routing.afprofile.zip"
        session.command("profile.stop", path=str(path), wait=True)
        (directory / "summary.json").write_text(json.dumps(report(path), indent=2))
        print(json.dumps(report(path)))
    finally:
        session.close()


if __name__ == "__main__":
    run(Path(sys.argv[1]).resolve(), int(sys.argv[2]) if len(sys.argv) > 2 else 100)
