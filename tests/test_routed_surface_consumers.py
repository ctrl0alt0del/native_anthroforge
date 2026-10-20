"""Adaptive exact membranes keep downstream fibers and required role semantics."""

import numpy as np
import pytest

from anthroforge.core.fibers import Fiber
from tests import routed_surface_scene as scene
from tests.test_fiber_creation import path
from tests.test_tissue_workflow import roundtrip


def target_tissue(session):
    objects = scene.create(session)
    target = session.command("tissue.create", source=objects["exact"], preset="CUSTOM")
    session.wait()
    return objects["supports"][-1], target


def fiber_on_target(session, target, role):
    source = session.command(
        "curve.create",
        engine="POLYLINE",
        points=[dict(position=[x, 0, 0.28]) for x in (-0.9, -0.6, -0.3)],
    )
    session.wait()
    points = session.document.object(source).points
    bindings = [dict(point=p.id, target=target, role=role) for p in (points[0], points[-1])]
    session.command("fiber.create", curve=source, bindings=bindings)
    session.wait()
    return next(o for o in reversed(session.document.objects) if isinstance(o, Fiber))


@pytest.mark.parametrize("role", ["TISSUE_BASE", "TISSUE_FINAL"])
def test_downstream_fiber_retains_dense_material_capture_during_routing(session, tmp_path, role):
    obstacle, target = target_tissue(session)
    fiber = fiber_on_target(session, target, role)
    initial = path(session, fiber.id).copy()
    scene.move(session, obstacle, [0, 0, 0])
    assert_fiber(session, fiber)
    assert not np.allclose(path(session, fiber.id)[:, :3], initial[:, :3])
    roundtrip(session, tmp_path / "downstream.anthroforge")
    scene.move(session, obstacle, [0, 0, 3])
    assert_fiber(session, fiber)
    np.testing.assert_allclose(path(session, fiber.id)[:, :3], initial[:, :3], atol=1e-8)
    assert not session.scheduler.errors


def assert_fiber(session, before):
    current = session.document.object(before.id)
    assert current.result.status == "ready", current.result.error
    assert current.bindings == before.bindings
    assert current.attachment_asset == before.attachment_asset
