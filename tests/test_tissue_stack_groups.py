"""Opposite side orders are atomic groups; actual construction cycles remain failures."""

import numpy as np

from anthroforge.application import dependencies
from anthroforge.core.results import Port
from tests.test_tissue_stack_workflow import assembly, current
from tests.test_tissue_workflow import roundtrip


def envelopes(session):
    _, first, second = assembly(session)
    for key in (first, second):
        session.command("tissue.configure", target=key, changes=dict(both_sides=True))
    for a, b in (("a", "b"), ("b", "a")):
        session.command(
            "tissue.stacking.relationship",
            target=first,
            other=second,
            side=a,
            other_side=b,
            excluded=True,
        )
    session.wait(30)
    return first, second


def test_opposite_side_orders_publish_complete_bundles_and_roundtrip(session, tmp_path):
    first, second = envelopes(session)
    for key in (first, second):
        current(session, key)
        assert Port(key, "final") not in dependencies.blocked(dependencies.graph(session.document))
    jobs = [job for job in session.scheduler.jobs if job.key.startswith("tissue:group:")]
    assert any(job.outputs == {first, second} and job.state == "succeeded" for job in jobs)
    session.command("tissue.stacking.configure", target=first, changes=dict(clearance=0.001))
    session.wait(30)
    before = {key: current(session, key) for key in (first, second)}
    roundtrip(session, tmp_path / "group.anthroforge")
    for key, points in before.items():
        np.testing.assert_array_equal(current(session, key), points)


def test_manual_member_keeps_final_until_explicit_evaluation(session):
    first, second = envelopes(session)
    before = current(session, first)
    session.command("update_mode", entity=first, mode="MANUAL")
    session.command("tissue.inflation", target=second, side="b", changes=dict(amount=0.04))
    session.wait(30)
    current(session, second)
    accepted = session.document.object(first).final_result
    assert accepted.status == "pending" and not accepted.error
    np.testing.assert_array_equal(session.assets[accepted.asset].mesh.array(0), before)
    session.command("evaluate", entities=[first])
    session.wait(30)
    assert current(session, first)[:, 2].min() < before[:, 2].min() - 0.001


def test_group_does_not_remove_a_true_attachment_cycle(session):
    first, second = envelopes(session)
    membrane = session.document.object(session.document.object(first).source)
    fiber = session.document.object(membrane.curves[0].curve)
    session.command(
        "fiber.binding.set",
        curve=fiber.id,
        point=fiber.points[0].id,
        target=second,
        role="TISSUE_FINAL",
    )
    session.wait(30)
    blocked = dependencies.blocked(dependencies.graph(session.document))
    assert Port(first, "final") in blocked and Port(second, "final") in blocked
    assert_failed_group(session, (first, second))


def assert_failed_group(session, keys):
    assert all(session.document.object(key).final_result.status == "failed" for key in keys)


def test_group_failure_retains_final_and_displays_current_intrinsic(session):
    first, second = envelopes(session)
    before = {key: session.document.object(key).final_result.asset for key in (first, second)}
    session.command("tissue.stacking.remove", target=first, other=second, side="a", other_side="b")
    session.wait(30)
    for key, asset in before.items():
        item = session.document.object(key)
        assert item.final_result.status == "failed" and item.final_result.asset == asset
        assert (
            item.result.status == "unstacked" and item.result.asset == item.intrinsic_result.asset
        )
    session.command("undo")
    session.wait(30)
    current(session, first)
    current(session, second)
