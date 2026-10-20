"""Real API fibers, membranes and tissue attachments for the sampling comparison."""

from pathlib import Path

from anthroforge.core.fibers import Fiber
from anthroforge.core.surfaces import Surface

ROOT = Path(__file__).resolve().parents[1]


def cube(session, parent, position):
    key = session.command(
        "import", path=str(ROOT / "examples/primitives/cube.obj"), units=1, parent=parent
    )["entity_id"]
    session.wait()
    move(session, key, position)
    return key


def move(session, key, position):
    session.command("scp.transform", entity=key, values=[*position, 0, 0, 0, 1, 1, 1])
    session.wait()


def fiber(session, parents, y):
    key = session.command(
        "curve.create",
        engine="ROUTED",
        settings=dict(samples=3),
        points=[dict(position=[x, y, 0.25]) for x in (-1.499999, 1.499999)],
    )
    session.wait()
    return bind(session, parents, key)


def bind(session, parents, key):
    bindings = [
        dict(point=p.id, target=t)
        for p, t in zip(session.document.object(key).points, parents, strict=True)
    ]
    session.command("fiber.create", curve=key, bindings=bindings)
    session.wait()
    result = next(o.id for o in reversed(session.document.objects) if isinstance(o, Fiber))
    session.command("object.delete", target=key)
    session.wait()
    return result


def surface(session, fibers, exact):
    session.command("surface.create", curves=fibers, strips=2, exact=exact)
    session.wait()
    return next(o.id for o in reversed(session.document.objects) if isinstance(o, Surface))


def attachment(session, tissue, role):
    point = session.command("construction.point.create", position=[-0.6, 0, 0.25])
    key = session.command("anchor.create", source=point, parent=tissue, role=role)["object_id"]
    session.wait()
    return key


def create(session):
    left = cube(session, "", [-2, 0, 0])
    right, obstacle = cube(session, left, [2, 0, 0]), cube(session, left, [0, 0, 3])
    fibers = [fiber(session, [left, right], y) for y in (-0.2, 0.2)]
    exact, uniform = [surface(session, fibers, mode) for mode in (True, False)]
    tissue = session.command("tissue.create", source=uniform, preset="CUSTOM")
    session.wait()
    anchors = [attachment(session, tissue, role) for role in ("TISSUE_BASE", "TISSUE_FINAL")]
    return context([left, right, obstacle], fibers, exact, uniform, tissue, anchors)


def context(supports, fibers, exact, uniform, tissue, anchors):
    return dict(
        supports=supports,
        fibers=fibers,
        exact=exact,
        uniform=uniform,
        tissue=tissue,
        anchors=anchors,
    )
