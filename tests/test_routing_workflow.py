"""Native routing through the shared command, dependency and persistence contracts."""

import numpy as np
import pytest

from anthroforge.application import storage
from tests.test_fiber_creation import CUBE, bind, path, scene


def create(session, obstacles=(), points=((-1, 0, 0), (1, 0, 0))):
    key = session.command(
        "curve.create",
        engine="ROUTED",
        points=[dict(position=p) for p in points],
        settings=dict(samples=32, obstacles=list(obstacles)),
    )
    session.wait(10)
    return key


def accepted(session, key):
    item = session.document.object(key)
    assert item.result.status == "ready", item.result.error
    return session.resources.paths[item.result.asset]


def convert(session, key):
    item = session.document.object(key)
    value = session.command(
        "curve.conversion.preview",
        curve=key,
        engine="ROUTED",
        mode="AUTHORED",
        points=[p.id for p in item.points],
    )
    session.wait(10)
    assert session.conversion.state == "ready", session.conversion.error
    session.command("curve.conversion.accept", token=value["token"])
    session.wait(10)
    return accepted(session, key)


def test_curve_only_route_uses_worker_and_roundtrips_without_rerouting(session, tmp_path):
    key = create(session)
    asset = accepted(session, key)
    job = next(j for j in session.scheduler.jobs if j.kind == "curve_routing")
    assert job.assessment.schedule.execution == "worker"
    filename = tmp_path / "route.anthroforge"
    storage.atomic_save(filename, session.document, session.resources)
    document, resources = storage.read_package(filename, session.engine)
    restored = resources.paths[document.object(key).result.asset]
    np.testing.assert_array_equal(restored.path.array(), asset.path.array())
    assert restored.diagnostics == asset.diagnostics


def test_obstacle_motion_invalidates_route_and_failure_retains_accepted_path(session):
    target = session.command("import", path=str(CUBE), units=0.6)["entity_id"]
    session.wait()
    key = create(session, (target,))
    before = accepted(session, key)
    session.command("scp.transform", entity=target, values=[2, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait(10)
    assert accepted(session, key).path.handle != before.path.handle
    retained = session.document.object(key).result.asset
    point = session.document.object(key).points[0].id
    session.command("curve.point.update", curve=key, point=point, position=[2, 0, 0])
    session.wait(10)
    result = session.document.object(key).result
    assert result.status == "failed" and result.asset == retained and result.error


def test_routed_fiber_edit_and_parent_motion_keep_bindings_and_source_independent(session):
    target, source = scene(session)
    fiber = bind(session, target, source)
    before = path(session, source)
    convert(session, fiber.id)
    edit_routing_point(session, fiber)
    changed = accepted(session, fiber.id)
    session.command("scp.transform", entity=target, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    session.wait(10)
    moved = accepted(session, fiber.id)
    np.testing.assert_allclose(
        moved.path.array()[[0, -1], :3], changed.path.array()[[0, -1], :3] + [0, 0, 1], atol=1e-10
    )
    assert session.document.object(fiber.id).bindings == fiber.bindings
    np.testing.assert_array_equal(path(session, source), before)


def edit_routing_point(session, fiber):
    session.command(
        "curve.point.update", curve=fiber.id, point=fiber.points[1].id, position=[0, 0.3, 0.9]
    )
    session.wait(10)


def test_routing_rejects_non_anatomical_obstacle_in_shared_model(session):
    curve = session.command("curve.create")
    session.wait()
    with pytest.raises(ValueError, match="surface providers"):
        create(session, (curve,))
