"""Surface-click creation publishes only a complete bound and routed Fiber."""

from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.fibers import Fiber

CUBE = Path(__file__).resolve().parents[1] / "examples/primitives/cube.obj"


def cube(session):
    target = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait()
    return target


def placed(session, target):
    session.command(
        "fiber.place",
        points=[
            dict(position=[-0.501, 0, 0], target=target),
            dict(position=[0.501, 0, 0], target=target),
        ],
    )
    session.wait()
    fibers = [o for o in session.document.objects if isinstance(o, Fiber)]
    assert len(fibers) == 1, [j.error for j in session.scheduler.jobs]
    return fibers[0]


def test_quick_fiber_routes_before_publication_and_is_one_undo(session):
    target = cube(session)
    count = len(session.history.entries)
    fiber = placed(session, target)
    assert session.document.objects == (fiber,) and fiber.engine == "ROUTED"
    assert len(fiber.bindings) == 2 and {b.target for b in fiber.bindings} == {target}
    path = session.resources.paths[fiber.result.asset].path.array()
    assert np.max(np.abs(path[:, 1:3])) >= 0.5
    assert len(session.history.entries) == count + 1
    session.navigate(-1)
    assert not session.document.objects
    session.navigate(1)
    session.wait()
    assert session.document.object(fiber.id).result.asset


def test_each_pin_keeps_its_explicit_surface_instead_of_nearest_default(session):
    first = cube(session)
    second = session.command("import", path=str(CUBE), parent=first, units=1.0)["entity_id"]
    session.wait()
    session.command(
        "fiber.place",
        points=[
            dict(position=[-0.4, 0, 0.503], target=second),
            dict(position=[0, 0, 0.503], target=first),
            dict(position=[0.4, 0, 0.503], target=second),
        ],
    )
    session.wait()
    assert session.document.objects, [(j.state, j.error) for j in session.scheduler.jobs if j.error]
    assert [b.target for b in session.document.objects[0].bindings] == [second, first, second]


def test_invalid_or_canceled_creation_leaves_no_orphan(session):
    target = cube(session)
    with pytest.raises(ValueError, match="clicked surface"):
        session.command("fiber.place", points=[dict(position=[0, 0, 0])] * 2)
    assert not session.document.objects
    job = session.command(
        "fiber.place",
        points=[
            dict(position=[-0.501, 0, 0], target=target),
            dict(position=[0.501, 0, 0], target=target),
        ],
    )
    session.scheduler.cancel_job(job)
    session.wait()
    assert not session.document.objects
