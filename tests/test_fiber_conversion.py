"""Previewed sampled conversions retain structural binding identities and parent choices."""

import numpy as np
import pytest

from tests.test_curve_conversion import preview
from tests.test_fiber_bindings import assign
from tests.test_fiber_creation import bind, path, scene


@pytest.mark.parametrize("closed", [False, True])
def test_sampled_conversion_retains_interior_bindings_and_one_undo(session, closed):
    target, source = scene(session, closed=closed)
    fiber = bind(session, target, source)
    before = assign(session, fiber.id, fiber.points[1].id, target)
    token = preview(session, fiber.id, samples=17)
    candidate = session.conversion.asset.authored
    assert len(candidate.points) == 17 and candidate.bindings == before.bindings
    verify_bound_positions(before, candidate)
    session.command("curve.conversion.accept", token=token)
    session.wait()
    assert session.document.object(fiber.id).result.status == "ready"
    parent_motion(session, target, fiber.id)
    session.navigate(-1)
    session.navigate(-1)
    assert session.document.object(fiber.id).points == before.points


def verify_bound_positions(before, after):
    points = {p.id: p for p in after.points}
    for point in before.points:
        if point.id in {b.point for b in before.bindings}:
            np.testing.assert_allclose(points[point.id].position, point.position, atol=1e-12)


def parent_motion(session, target, fiber):
    shape = path(session, fiber)
    session.command("scp.transform", entity=target, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(path(session, fiber)[:, :3], shape[:, :3] + [0, 0, 1], atol=1e-12)
