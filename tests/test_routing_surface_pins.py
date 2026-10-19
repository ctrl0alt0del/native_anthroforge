"""User scene: independent routing knots touch two cubes without anatomical bindings."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.native import path_collisions, paths, routing
from tests.test_fiber_creation import CUBE

CASE = json.loads((Path(__file__).parent / "fixtures/routing/surface_pins.json").read_text())


def colliders(session):
    return [
        session.engine.create_mesh(
            s["vertices"], np.array(s["triangles"]).ravel(), np.arange(len(s["triangles"]) + 1) * 3
        )
        for s in CASE["surfaces"]
    ]


def inputs(session):
    meshes = colliders(session)
    curve = Curve(
        tuple(CurvePoint(position=tuple(p)) for p in CASE["points"]),
        engine_settings=RoutingSettings(),
    )
    return meshes, routing.Inputs(
        curve,
        tuple(m.handle for m in meshes),
        tuple(tuple(s["matrix"]) for s in CASE["surfaces"]),
        tuple(CASE["matrix"]),
    )


@pytest.mark.parametrize("warm", [False, True])
def test_surface_contacts_route_without_binding_and_recover_obsolete_seed(session, warm):
    meshes, value = inputs(session)
    previous = paths.restore(session.engine, **CASE["previous"], closed=False)
    value = replace(value, warm=previous if warm else None)
    result, _ = routing.evaluate(session.engine, value)
    expected, _ = routing.evaluate(session.engine, replace(value, owners=tuple(CASE["contacts"])))
    np.testing.assert_allclose(result.array(), expected.array(), atol=1e-10, rtol=0)
    assert not np.allclose(result.array(), previous.array())
    for i, point in enumerate(value.curve.points):
        np.testing.assert_allclose(result.array()[result.array(1) == i, :3], [point.position])
    row = path_collisions.row(result, value.world, CASE["contacts"])
    collisions, _ = path_collisions.check(session.engine, [row], value.handles, value.matrices)
    assert np.all(collisions < 0), collisions
    assert type(value.curve) is Curve and not value.owners


@pytest.mark.parametrize("offset", [-0.01, 0.001])
def test_contact_detection_does_not_exempt_inside_or_merely_nearby_pins(session, offset):
    meshes, value = inputs(session)
    first = value.curve.points[0]
    position = (*first.position[:2], first.position[2] + offset)
    curve = replace(
        value.curve, points=(replace(first, position=position), *value.curve.points[1:])
    )
    with pytest.raises(ValueError, match="intersects an unrelated surface"):
        routing.evaluate(session.engine, replace(value, curve=curve))


def test_explicit_binding_contact_is_not_silently_changed(session):
    meshes, value = inputs(session)
    with pytest.raises(ValueError, match="intersects an unrelated surface"):
        routing.evaluate(session.engine, replace(value, owners=(2, 2, 1)))


def scene(session):
    root = session.command("import", path=str(CUBE), units=1)["entity_id"]
    session.wait(10)
    child = session.command("import", path=str(CUBE), units=1, parent=root)["entity_id"]
    session.wait(10)
    values = session.engine.decompose(CASE["surfaces"][1]["matrix"])
    session.command("scp.transform", entity=child, values=values)
    curve = session.command(
        "curve.create",
        engine="ROUTED",
        points=[dict(position=p) for p in CASE["points"]],
        values=session.engine.decompose(CASE["matrix"]),
    )
    session.wait(10)
    return root, child, curve


def test_enabling_obstacles_on_saved_straight_curve_updates_and_undoes(session, tmp_path):
    root, child, key = scene(session)
    original = session.document.object(key)
    session.command("curve.engine_settings", curve=key, obstacles=[root, child])
    session.wait(10)
    curve = session.document.object(key)
    assert curve.result.status == "ready", curve.result.error
    assert curve.result.asset != original.result.asset and curve.points == original.points
    session.command("save", path=str(tmp_path / "routed.anthroforge"), blocked_policy="wait")
    session.command("undo")
    session.wait(10)
    assert not session.document.object(key).engine_settings.obstacles
    session.command("redo")
    session.wait(10)
    assert session.document.object(key).result.status == "ready"
