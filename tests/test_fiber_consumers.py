"""Curve consumers retain resolved shape when applying their own control deformers."""

import numpy as np

from tests.test_fiber_creation import CUBE
from tests.test_primitives import mesh


def differential_fiber(session):
    first, second = supports(session)
    source = session.command(
        "curve.create", points=[dict(position=[x, 0, 0.7]) for x in (0, 0.75, 1.5)]
    )
    session.wait()
    points = session.document.object(source).points
    bindings = [
        dict(point=p.id, target=t)
        for p, t in zip((points[0], points[-1]), (first, second), strict=True)
    ]
    session.command("fiber.create", curve=source, bindings=bindings)
    session.wait()
    session.command("scp.transform", entity=second, values=[1.5, 0, 1, 0, 0, 0, 1, 1, 1])
    session.wait()
    return first, session.document.objects[-1].id


def supports(session):
    first = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait()
    second = session.command("import", path=str(CUBE), units=1.0, parent=first)["entity_id"]
    session.wait()
    session.command("scp.transform", entity=second, values=[1.5, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait()
    return first, second


def test_stationary_hook_preserves_differential_attachment_deformation(session):
    parent, fiber = differential_fiber(session)
    body = session.command("primitive.from_curves", curves=[fiber], kind="BODY", parent=parent)
    session.wait()
    before = mesh(session, body).array(0).copy()
    control = session.command("control.create", entity=body)
    session.command(
        "deformer.add", control=control, target=dict(owner=body, stage="CURVE", component=fiber)
    )
    session.wait()
    assert session.document.entity(body).result.status == "ready"
    np.testing.assert_allclose(mesh(session, body).array(0), before, atol=1e-12)
