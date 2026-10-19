"""Shared API integration exercises detected provider dependencies and accepted final surfaces."""

import numpy as np

from anthroforge.application import dependencies
from anthroforge.core.results import Port
from tests.conftest import CUBE
from tests.test_fiber_creation import bind
from tests.test_surface_workflow import surface
from tests.test_tissue_workflow import roundtrip


def fiber(session, bone, y, z):
    source = session.command(
        "curve.create", engine="POLYLINE", points=[dict(position=[x, y, z]) for x in (-0.4, 0, 0.4)]
    )
    session.wait(20)
    return bind(session, bone, source).id


def layer(session, membrane):
    tissue = session.command("tissue.create", source=membrane)
    session.wait(30)
    return tissue


def assembly(session):
    bone = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait(20)
    sources = [
        surface(session, [fiber(session, bone, y, z) for y in (0.3, -0.3)], strips=6)
        for z in (0.7, 0.71)
    ]
    return bone, layer(session, sources[0]), layer(session, sources[1])


def current(session, key):
    item = session.document.object(key)
    assert item.final_result.status == "ready", (item.final_result.error, session.scheduler.errors)
    assert item.final_material is not None
    return session.assets[item.final_result.asset].mesh.array(0).copy()


def test_automatic_stacking_creates_provider_first_dependencies(session):
    _, first, second = assembly(session)
    a, b = session.document.object(first), session.document.object(second)
    assert not a.stack_plan.providers and b.stack_plan.providers == (first,)
    graph = dependencies.graph(session.document)
    assert Port(first, "final") in graph[Port(second, "final")]
    assert Port(second, "intrinsic") not in dependencies.ports(
        session.document, Port(first, "final")
    )
    intrinsic = session.assets[b.intrinsic_result.asset].mesh.array(0)
    assert np.max(current(session, second)[:, 2] - intrinsic[:, 2]) > 0.001
    np.testing.assert_allclose(
        current(session, first), session.assets[a.intrinsic_result.asset].mesh.array(0)
    )


def test_manual_provider_keeps_accepted_output_until_explicit_evaluation(session):
    _, first, second = assembly(session)
    before = current(session, second)
    session.command("update_mode", entity=first, mode="MANUAL")
    session.command("tissue.inflation", target=first, changes=dict(amount=0.05))
    session.wait(30)
    np.testing.assert_array_equal(current(session, second), before)
    session.command("evaluate", entities=[first])
    session.wait(30)
    assert np.max(current(session, second)[:, 2] - before[:, 2]) > 0.005


def test_stacking_only_change_keeps_intrinsic_and_reuses_unchanged_final(session):
    _, first, _ = assembly(session)
    before = session.document.object(first)
    session.command("tissue.configure", target=first, changes=dict(stacking=False))
    session.wait(30)
    after = session.document.object(first)
    assert after.intrinsic_result == before.intrinsic_result
    assert after.final_result.asset == before.final_result.asset


def test_exclusion_roundtrip_and_removal_restore_automatic_order(session, tmp_path):
    _, first, second = assembly(session)
    before = current(session, second)
    session.command("tissue.stacking.relationship", target=second, other=first, excluded=True)
    session.wait(30)
    item = session.document.object(second)
    assert not item.stack_plan.providers and item.stack_relationships[0].excluded
    np.testing.assert_allclose(
        current(session, second), session.assets[item.intrinsic_result.asset].mesh.array(0)
    )
    roundtrip(session, tmp_path / "stacking.anthroforge")
    assert session.document.object(second).stack_relationships == item.stack_relationships
    session.command("tissue.stacking.remove", target=second, other=first)
    session.wait(30)
    np.testing.assert_allclose(current(session, second), before, atol=1e-10)


def test_failed_stacking_displays_current_intrinsic_and_blocks_final_surface(session):
    _, first, second = assembly(session)
    original = session.document.object(second)
    session.command(
        "tissue.stacking.relationship", target=second, other=first, mode="REQUESTED", cover="OTHER"
    )
    session.wait(30)
    failed = session.document.object(second)
    assert failed.final_result.status == "failed" and failed.result.status == "unstacked"
    assert failed.result.asset == failed.intrinsic_result.asset
    assert failed.final_result.asset == original.final_result.asset
    assert "ORDER_CONFLICT" in failed.final_result.error


def test_disabled_inflation_and_empty_crop_publish_own_output(session):
    _, first, second = assembly(session)
    session.command("tissue.inflation", target=second, changes=dict(enabled=False))
    session.wait(30)
    item = session.document.object(second)
    assert item.final_result.status == "ready" and not item.stack_plan.providers
    np.testing.assert_allclose(
        current(session, second), session.assets[item.intrinsic_result.asset].mesh.array(0)
    )
    session.command("tissue.crop", target=first, changes=dict(enabled=True, origin=[100, 0, 0]))
    session.wait(30)
    assert current(session, first).shape == (0, 3)
