"""Direct workflows preserve attachment intent, shared deletion policy and one-action undo."""

import pytest

from anthroforge.core.fibers import Fiber
from tests.test_fiber_creation import CUBE, bind, scene


def last_fiber(session):
    session.wait()
    fibers = [item for item in session.document.objects if isinstance(item, Fiber)]
    assert fibers, session.scheduler.errors
    return fibers[-1]


@pytest.mark.parametrize("closed, count", [(False, 2), (True, 1)])
def test_default_capture_is_independent_and_one_undo(session, closed, count):
    target, source = scene(session, closed)
    original = session.document.object(source)
    before = len(session.history.entries)
    session.command("fiber.create", curve=source)
    fiber = last_fiber(session)
    assert len(fiber.bindings) == count
    assert {b.target for b in fiber.bindings} == {target}
    assert session.document.object(source) == original
    assert len(session.history.entries) == before + 1
    session.navigate(-1)
    assert fiber.id not in session.document.registry.records
    session.navigate(1)
    session.wait()
    assert session.document.object(fiber.id).bindings == fiber.bindings


def two_surfaces(session):
    root, _ = scene(session)
    other = session.command("import", path=str(CUBE), units=1.0, parent=root)["entity_id"]
    session.wait()
    session.command("scp.transform", entity=other, values=[8, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait()
    source = session.command(
        "curve.create", points=[dict(position=p) for p in [[0.6, 0, 0], [7.4, 0, 0]]]
    )
    session.wait()
    return root, other, source


def test_default_capture_chooses_a_different_nearest_surface_per_endpoint(session):
    root, other, source = two_surfaces(session)
    session.command("fiber.create", curve=source)
    fiber = last_fiber(session)
    assert [b.target for b in fiber.bindings] == [root, other]
    assert {b.role for b in fiber.bindings} == {"SCP_GEOMETRY"}


def test_explicit_override_and_automatic_pin_can_be_mixed(session):
    root, other, source = two_surfaces(session)
    first, last = session.document.object(source).points
    session.command(
        "fiber.create",
        curve=source,
        bindings=[dict(point=first.id, target=other), dict(point=last.id)],
    )
    assert [b.target for b in last_fiber(session).bindings] == [other, other]
    assert root != other


def test_default_capture_reports_missing_surfaces_without_history_or_objects(session):
    source = session.command("curve.create")
    session.wait()
    before, count = session.document, len(session.history.entries)
    with pytest.raises(ValueError, match="No ready SCP surfaces"):
        session.command("fiber.create", curve=source)
    assert session.document == before and len(session.history.entries) == count


def test_delete_impact_distinguishes_leaf_from_parent_without_mutation(session, assembly):
    root, child = assembly
    before, count = session.document, len(session.history.entries)
    leaf = session.command("object.delete.inspect", target=child)
    parent = session.command("object.delete.inspect", target=root)
    assert not leaf["affected"]
    assert child in {row["id"] for row in parent["affected"]}
    assert session.document == before and len(session.history.entries) == count


def test_delete_impact_rejects_bound_anatomical_support(session):
    target, source = scene(session)
    bind(session, target, source)
    with pytest.raises(ValueError, match="Rebind dependent anatomy"):
        session.command("object.delete.inspect", target=target)


def test_delete_impact_counts_ordinary_parenting_and_workspace_ownership(session):
    root = session.command("scp.empty", name="Root")
    child = session.command("curve.create", parent=root)
    associated = session.command("curve.create", owner=root)
    session.wait()
    affected = session.command("object.delete.inspect", target=root)["affected"]
    assert {child, associated}.issubset({row["id"] for row in affected})
