"""Build the skull routing fixture through the same public operations as desktop authoring."""

import json
from pathlib import Path

from anthroforge.core.fibers import Fiber

FIXTURE = Path("tests/fixtures/routing/skull.json")


def mesh_file(folder, item):
    path = folder / (item["name"] + ".obj")
    vertices = ["v " + " ".join(map(str, point)) for point in item["vertices"]]
    faces = ["f " + " ".join(str(i + 1) for i in face) for face in item["triangles"]]
    path.write_text("\n".join((*vertices, *faces)) + "\n")
    return path


def import_meshes(session, folder, fixture):
    keys = []
    for item in fixture["colliders"]:
        path = mesh_file(folder, item)
        key = session.command("import", path=str(path), units=1.0, parent=keys[0] if keys else "")
        session.wait(15)
        keys.append(key["entity_id"])
    return keys


def fiber(session, case, targets):
    source = session.command(
        "curve.create", engine="POLYLINE", points=[dict(position=p) for p in case["points"]]
    )
    session.wait(15)
    bindings = [
        dict(point=p.id, target=targets[owner - 1])
        for p, owner in zip(session.document.object(source).points, case["owners"], strict=True)
    ]
    session.command("fiber.create", curve=source, bindings=bindings, name=case["name"])
    session.wait(15)
    item = next(o for o in reversed(session.document.objects) if isinstance(o, Fiber))
    convert(session, item, targets)
    session.command("object.delete", target=source)
    return item.id


def convert(session, item, targets):
    preview = session.command(
        "curve.conversion.preview",
        curve=item.id,
        engine="ROUTED",
        mode="AUTHORED",
        points=[p.id for p in item.points],
        settings=dict(samples=64, obstacles=targets),
    )
    session.wait(15)
    status = session.command("curve.conversion.status")
    assert status["state"] == "ready", status
    session.command("curve.conversion.accept", token=preview["token"])
    session.wait(15)
    assert session.document.object(item.id).result.status == "ready"


def create(session, folder):
    folder.mkdir(parents=True, exist_ok=True)
    fixture = json.loads(FIXTURE.read_text())
    targets = import_meshes(session, folder, fixture)
    curves = [fiber(session, case, targets) for case in fixture["cases"]]
    session.command("surface.create", curves=curves[:2], name="Scalp fiber loft", strips=7)
    session.wait(15)
    return targets, curves
