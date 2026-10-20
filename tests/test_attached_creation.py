"""Automatic construction conversion is atomic, independent and uses shared binding semantics."""

import numpy as np
import pytest

from anthroforge.core.fibers import Fiber
from anthroforge.core.membranes import Membrane
from anthroforge.core.points import Anchor
from anthroforge.core.tissues import TissueVCP
from tests.test_fiber_creation import path, scene


def created(session, operation, **arguments):
    result = session.command(operation, **arguments)
    target = result["object_id"] if isinstance(result, dict) else result
    job = session.scheduler.registry.by_id.get(target)
    if job:
        target = next(iter(job.outputs))
    session.wait()
    assert not session.scheduler.errors, session.scheduler.errors
    return session.document.object(target)


def surface_scene(session):
    target, first = scene(session)
    second = session.command(
        "curve.create",
        points=[dict(position=p) for p in [[-0.4, 0.3, 0.7], [0, 0.5, 0.8], [0.4, 0.3, 0.7]]],
    )
    session.wait()
    surface = created(session, "surface.create", curves=[first, second])
    return target, surface, (first, second)


def test_point_tissue_converts_to_anchor_once(session):
    target, _ = scene(session)
    source = session.command("construction.point.create", position=[0, 0, 0.7])
    original, cursor = session.document.object(source), session.history.cursor
    item = created(session, "tissue.create", source=source)
    anchor = session.document.object(item.source)
    assert isinstance(item, TissueVCP) and isinstance(anchor, Anchor)
    assert anchor.binding.reference.target == target and anchor.id != source
    assert session.document.object(source) == original
    assert session.history.cursor == cursor + 1 and item.result.asset
    undo_redo(session, item, anchor)


def undo_redo(session, item, anchor):
    session.command("undo")
    assert not {anchor.id, item.id} & session.document.registry.records.keys()
    session.command("redo")
    session.wait()
    assert session.document.object(item.id).source == anchor.id


@pytest.mark.parametrize("closed", [False, True])
def test_curve_tissue_keeps_visible_path_and_original(session, closed):
    target, source = scene(session, closed)
    original, before = session.document.object(source), path(session, source)
    item = created(session, "tissue.create", source=source)
    fiber = session.document.object(item.source)
    assert isinstance(fiber, Fiber) and {b.target for b in fiber.bindings} == {target}
    np.testing.assert_array_equal(path(session, fiber.id), before)
    assert session.document.object(source) == original
    assert not {p.id for p in fiber.points} & {p.id for p in original.points}
    assert item.result.asset


@pytest.mark.parametrize("operation", ["membrane.create", "tissue.create"])
def test_surface_conversion_is_independent_and_keeps_geometry(session, operation):
    _, source, curves = surface_scene(session)
    originals, cursor = session.document.objects, session.history.cursor
    before = session.assets[source.result.asset].mesh.array(0).copy()
    item = created(session, operation, source=source.id)
    membrane = session.document.object(item.source) if isinstance(item, TissueVCP) else item
    assert isinstance(membrane, Membrane)
    assert all(isinstance(session.document.object(u.curve), Fiber) for u in membrane.curves)
    assert not {u.curve for u in membrane.curves} & set(curves)
    np.testing.assert_allclose(session.assets[membrane.result.asset].mesh.array(0), before)
    assert all(session.document.object(o.id) == o for o in originals)
    assert session.history.cursor == cursor + 1
    session.command("undo")
    assert session.document.objects == originals


def test_missing_scp_rejects_without_partial_construction(session):
    source = session.command("curve.create")
    session.wait()
    before, cursor = session.document, session.history.cursor
    with pytest.raises(ValueError, match="No ready SCP"):
        session.command("tissue.create", source=source)
    assert session.document == before and session.history.cursor == cursor


def test_automatic_anchor_creation_uses_same_nearest_default(session):
    target, _ = scene(session)
    source = session.command("construction.point.create", position=[0, 0, 0.7])
    anchor = created(session, "anchor.create", source=source)
    assert anchor.binding.reference.target == target
