"""The actual Curve subclass participates in ordinary transactions, propagation and saving."""

from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.construction import Curve
from anthroforge.core.fibers import Fiber

CUBE = Path(__file__).resolve().parents[1] / "examples/primitives/cube.obj"


def scene(session, closed=False):
    target = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait()
    positions = [[-0.4, 0, 0.7], [0, 0.25, 0.8], [0.4, 0, 0.7]]
    source = session.command(
        "curve.create", points=[dict(position=p) for p in positions], closed=closed
    )
    session.wait()
    return target, source


def bind(session, target, source):
    curve = session.document.object(source)
    points = curve.points[:1] if curve.closed else (curve.points[0], curve.points[-1])
    session.command(
        "fiber.create", curve=source, bindings=[dict(point=p.id, target=target) for p in points]
    )
    session.wait()
    fibers = [item for item in session.document.objects if isinstance(item, Fiber)]
    assert fibers, [job.error for job in session.scheduler.jobs.values()]
    return fibers[-1]


def path(session, curve):
    item = session.document.object(curve)
    return session.resources.paths[item.result.asset].path.array().copy()


def test_creation_is_an_independent_curve_subclass_with_one_undo(session):
    target, source = scene(session)
    original, count = session.document.object(source), len(session.history.entries)
    fiber = bind(session, target, source)
    assert isinstance(fiber, Curve) and len(session.document.entities) == 1
    assert session.document.object(source) == original
    assert not {p.id for p in original.points} & {p.id for p in fiber.points}
    np.testing.assert_allclose(path(session, source), path(session, fiber.id))
    assert len(session.history.entries) == count + 1
    session.navigate(-1)
    assert fiber.id not in session.document.registry.records
    session.navigate(1)
    session.wait()
    assert session.document.object(fiber.id).attachment_asset


@pytest.mark.parametrize("closed", [False, True])
def test_parent_motion_resolves_dense_nodes_and_never_changes_source(session, closed):
    target, source = scene(session, closed)
    fiber = bind(session, target, source)
    before, original = path(session, fiber.id), path(session, source)
    session.command("scp.transform", entity=target, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    session.wait()
    moved = session.document.object(fiber.id)
    assert moved.result.revision > fiber.result.revision, moved.result.error
    np.testing.assert_allclose(
        path(session, fiber.id)[:, :3], before[:, :3] + [0, 0, 1], atol=1e-12
    )
    np.testing.assert_array_equal(path(session, source), original)
    assert moved.bindings == fiber.bindings and moved.attachment_asset == fiber.attachment_asset


def test_creation_rejects_unbound_open_draft_without_adding_an_object(session):
    target, source = scene(session)
    curve = session.document.object(source)
    with pytest.raises(ValueError, match="both open endpoints"):
        session.command(
            "fiber.create", curve=source, bindings=[dict(point=curve.points[0].id, target=target)]
        )
    assert session.document.objects == (curve,)


def test_fiber_roundtrip_keeps_bindings_and_editable_curve(session, tmp_path):
    target, source = scene(session)
    fiber = bind(session, target, source)
    location = tmp_path / "fiber.anthroforge"
    session.command("save", path=str(location), blocked_policy="wait")
    session.wait()
    session.command("open", path=str(location))
    session.wait()
    loaded = session.document.object(fiber.id)
    assert loaded.points == fiber.points and loaded.bindings == fiber.bindings
    session.command("scp.transform", entity=target, values=[0, 0, 2, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(
        path(session, fiber.id)[:, :3], path(session, source)[:, :3] + [0, 0, 2], atol=1e-12
    )
