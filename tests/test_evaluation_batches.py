"""Pose batching must not contract geometry dependencies into false cycles."""

from anthroforge.application.evaluation_batches import groups
from tests.test_construction_contracts import create, hook, mesh


def test_plain_pose_hierarchy_retains_batching(session):
    root = session.command("scp.empty", name="Root")
    child = session.command("scp.empty", parent=root, name="Child")
    session.wait(timeout=3)
    assert groups(session.document, {root, child}) == [{root, child}]


def test_full_evaluation_crosses_pose_geometry_boundaries(session):
    parent = create(session)
    hook(session, parent)
    child = create(session, parent)
    hook(session, child)
    leaf = create(session, child)
    for key in (child, leaf):
        session.command("scp.attachment", entity=key, parent_mode="SURFACE_NEAREST")
    session.wait(timeout=5)
    batches = groups(session.document, {parent, child, leaf})
    assert len(batches) == 3
    session.command("evaluate")
    session.wait(timeout=5)
    assert not session.scheduler.errors


def test_actual_cycles_finish_without_holding_unrelated_batches(session):
    parent = create(session)
    control = hook(session, parent)
    child = create(session, parent)
    session.command("control.follow", control=control, entity=control)
    session.command("evaluate")
    session.wait(timeout=5)
    assert session.document.entity(parent).result.status == "failed"
    assert not session.scheduler.blocked
    assert mesh(session, child).counts[0] > 0
