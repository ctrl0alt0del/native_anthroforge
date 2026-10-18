"""Small shared-junction fixture for invisible desktop branch acceptance."""

import json
from pathlib import Path

from anthroforge.core.surfaces import Surface


def create(session):
    case = json.loads(Path("tests/fixtures/surfaces/branches.json").read_text())["cases"][0]
    keys = [
        session.command("curve.create", points=[dict(position=p) for p in row], engine="POLYLINE")
        for row in case["rows"]
    ]
    session.wait()
    connect(session, keys)
    session.command("surface.create", curves=keys[:2], name="Branched construction")
    session.wait()
    return keys, next(o.id for o in session.document.objects if isinstance(o, Surface))


def connect(session, keys):
    for index, key in enumerate(keys[2:], 1):
        main, child = session.document.object(keys[0]), session.document.object(key)
        session.command(
            "junction.create",
            source=dict(curve=main.id, point=main.points[index].id),
            targets=[dict(curve=child.id, point=child.points[0].id)],
        )
    session.wait()
