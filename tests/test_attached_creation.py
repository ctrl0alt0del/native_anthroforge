"""Automatic construction conversion is atomic, independent and uses shared binding semantics."""

import numpy as np
import pytest

from anthroforge.core.fibers import Fiber
from anthroforge.core.membranes import Membrane
from anthroforge.core.points import Anchor
from anthroforge.core.tissues import TissueVCP
from tests.test_fiber_creation import path, scene
from tests.test_surface_workflow import surface, vertices


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


def test_surface_conversion_with_radial_and_swept_targets_after_reopen(session, tmp_path):
    _, source, curves = surface_scene(session)
    created(session, "tissue.create", source=curves[0], preset="RIM")
    point = session.command("construction.point.create", position=[0, 0, 0.8])
    created(session, "tissue.create", source=point, preset="CLOSED_BULK")
    path = tmp_path / "mixed-targets.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    session.command("open", path=str(path))
    item = created(session, "membrane.create", source=source.id)
    assert isinstance(item, Membrane) and item.result.status == "ready"
    assert all(isinstance(session.document.object(u.curve), Fiber) for u in item.curves)


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


@pytest.mark.parametrize("role", ["TISSUE_BASE", "TISSUE_FINAL", "UNKNOWN"])
def test_automatic_anchor_does_not_substitute_a_requested_surface_role(session, role):
    scene(session)
    source = session.command("construction.point.create", position=[0, 0, 0.7])
    before, cursor = session.document, session.history.cursor
    with pytest.raises(ValueError, match="explicit parent"):
        session.command("anchor.create", source=source, role=role)
    assert session.document == before and session.history.cursor == cursor


def test_mixed_surface_preserves_existing_fiber_binding_intent(session):
    _, first = scene(session)
    session.command("fiber.create", curve=first)
    session.wait()
    existing = next(o for o in session.document.objects if isinstance(o, Fiber))
    second = session.command(
        "curve.create", points=[dict(position=p) for p in [[-0.4, 0.3, 0.7], [0.4, 0.3, 0.7]]]
    )
    session.wait()
    source = surface(session, [existing.id, second])
    membrane = created(session, "membrane.create", source=source)
    copy = session.document.object(membrane.curves[0].curve)
    assert copy.id != existing.id and copy.supports == existing.supports
    assert [b.attachment for b in copy.bindings] == [b.attachment for b in existing.bindings]
    np.testing.assert_array_equal(path(session, copy.id), path(session, existing.id))


def test_branch_conversion_preserves_seams_and_copies_junctions_once(session):
    from tests.test_surface_branches import branched

    scene(session)
    _, source, _ = branched(session)
    original, joints = vertices(session, source), session.document.junctions
    membrane = created(session, "membrane.create", source=source)
    assert membrane.kind == "BRANCHED"
    assert len(session.document.junctions) == 2 * len(joints)
    np.testing.assert_allclose(vertices(session, membrane.id), original, atol=1e-12)
    assert {b.id for b in membrane.branches}.isdisjoint(
        session.document.object(source).accepted_parts
    )
    assert all(isinstance(session.document.object(u.curve), Fiber) for u in membrane.curves)


def test_new_membrane_follows_bone_and_is_independent_of_original_curves(session):
    target, source, curves = surface_scene(session)
    membrane = created(session, "membrane.create", source=source.id)
    initial, original = vertices(session, membrane.id), vertices(session, source.id)
    session.command("scp.transform", entity=target, values=[0, 0, 0.2, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(vertices(session, membrane.id), initial + [0, 0, 0.2], atol=1e-10)
    np.testing.assert_array_equal(vertices(session, source.id), original)
    item = session.document.object(curves[0])
    session.command(
        "curve.point.update", curve=item.id, point=item.points[0].id, position=[-0.5, 0, 0.7]
    )
    session.wait()
    np.testing.assert_allclose(vertices(session, membrane.id), initial + [0, 0, 0.2], atol=1e-10)


def test_converted_surface_roundtrips_without_recomputation(session, tmp_path):
    _, source, _ = surface_scene(session)
    tissue = created(session, "tissue.create", source=source.id)
    before = session.document.objects
    location = tmp_path / "automatic.anthroforge"
    session.command("save", path=str(location), blocked_policy="wait")
    session.wait()
    session.command("open", path=str(location))
    session.wait()
    assert session.document.objects == before
    assert session.document.object(tissue.id).result.asset in session.assets
