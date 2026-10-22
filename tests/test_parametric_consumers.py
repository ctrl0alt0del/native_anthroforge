"""Generated points participate in ordinary consumer and attachment contracts."""

import numpy as np
import pytest

from anthroforge.application import curve_copy
from anthroforge.core.fibers import Fiber
from tests.conftest import CUBE
from tests.test_fiber_creation import bind, path
from tests.test_junction_workflow import reference
from tests.test_parametric_curves import circle_settings, create, positions
from tests.test_shared_curves import vertices


def imported(session):
    target = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait()
    return target


@pytest.mark.parametrize("closed", [False, True])
def test_fiber_copy_is_exact_independent_and_follows_attachment(session, closed):
    target = imported(session)
    key = session.command(
        "curve.create", engine="PARAMETRIC", closed=closed, settings=circle_settings()
    )
    session.wait()
    before = path(session, key)
    fiber = bind(session, target, key)
    assert fiber.engine == "BEZIER" and fiber.closed == closed
    assert not fiber.parametric_definition
    np.testing.assert_array_equal(path(session, fiber.id), before)
    session.command("scp.transform", entity=target, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(path(session, fiber.id)[:, :3], before[:, :3] + [0, 0, 1], atol=1e-12)
    np.testing.assert_array_equal(path(session, key), before)


def test_fiber_capture_uses_dispatched_resolution_and_endpoint_intent(session):
    imported(session)
    key = create(session, resolution=5)
    session.command("curve.parametric.configure", curve=key, changes=dict(resolution=11))
    session.command("fiber.create", curve=key)
    session.wait()
    fiber = next(o for o in session.document.objects if isinstance(o, Fiber))
    assert len(fiber.points) == 11, session.scheduler.errors
    assert {b.point for b in fiber.bindings} == {fiber.points[0].id, fiber.points[-1].id}
    np.testing.assert_array_equal(path(session, fiber.id), path(session, key))


def test_shared_body_consumer_updates_from_equations_without_changing_source(session):
    key = create(session, resolution=11)
    body = session.command("primitive.from_curves", curves=[key], kind="BODY")
    session.wait()
    before = vertices(session, body)
    session.command("curve.parametric.configure", curve=key, changes=dict(y="t*t*m"))
    session.wait()
    assert not session.scheduler.errors
    assert not np.allclose(vertices(session, body), before)
    np.testing.assert_allclose(positions(session, key)[:, 1], np.linspace(0, 1, 11) ** 2)


def joined(session):
    a, b = create(session, resolution=3), session.command("curve.create")
    session.wait()
    joint = session.command(
        "junction.create", source=reference(session, b), targets=[reference(session, a)]
    )
    session.wait()
    return a, b, joint


def test_parametric_junction_drives_follower_and_locks_resolution(session):
    a, b, joint = joined(session)
    with pytest.raises(ValueError, match="junction"):
        session.command("curve.parametric.configure", curve=a, changes=dict(resolution=7))
    session.command("curve.parametric.configure", curve=a, changes=dict(x="(t+1)*m"))
    session.wait()
    np.testing.assert_allclose(positions(session, b)[0], positions(session, a)[0])
    with pytest.raises(ValueError, match="formula-controlled"):
        session.command(
            "curve.point.update", curve=b, point=reference(session, b)["point"], position=[2, 0, 0]
        )
    session.command("junction.remove", junction=joint)
    session.command("curve.parametric.configure", curve=a, changes=dict(resolution=7))
    session.wait()
    assert len(session.document.object(a).points) == 7


def test_independent_copy_remaps_variable_identities_in_active_and_stored_definitions(session):
    key = create(session, **circle_settings())
    source = session.document.object(key)
    copy = curve_copy.clone(source, curve_copy.mapping(source))
    assert copy.engine_settings.variables[0].id != source.engine_settings.variables[0].id
    session.command("curve.engine", curve=key, engine="BEZIER")
    source = session.document.object(key)
    copy = curve_copy.clone(source, curve_copy.mapping(source))
    assert (
        copy.parametric_definition.variables[0].id != source.parametric_definition.variables[0].id
    )
