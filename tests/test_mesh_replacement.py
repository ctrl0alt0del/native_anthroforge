"""Revision-checked mesh replacement preserves identity and exposes destructive changes."""

import numpy as np
import pytest

from tests.conftest import CUBE


def source(session):
    target = session.command("import", path=str(CUBE), units=1)["entity_id"]
    session.wait(5)
    return target


def assessment(session, target, path):
    result = session.command("scp.mesh.replace.assess", target=target, path=str(path))
    session.wait(10)
    state = session.command("scp.mesh.replace.status")
    assert state["state"] == "ready", state
    return result["token"], state


def test_same_mesh_replacement_keeps_identity_and_one_undo(session):
    target = source(session)
    before, cursor = session.document.entity(target), session.history.cursor
    token, state = assessment(session, target, CUBE)
    assert session.document.entity(target) == before and session.history.cursor == cursor
    assert state["matching_topology"] and not state["changes"]
    session.command("scp.mesh.replace.apply", token=token)
    session.wait(10)
    after = session.document.entity(target)
    assert after.result.status == "ready", after.result.error
    assert after.id == before.id and after.matrix == before.matrix
    assert after.primitive.source != before.primitive.source
    assert session.history.cursor == cursor + 1
    session.command("undo")
    assert session.document.entity(target).primitive == before.primitive


def tetrahedron(tmp_path):
    path = tmp_path / "tetra.obj"
    path.write_text("v 0 0 0\nv 1 0 0\nv 0 1 0\nv 0 0 1\nf 1 3 2\nf 1 2 4\nf 2 3 4\nf 3 1 4\n")
    return path


def test_changed_source_requires_explicit_approval_for_child_rebind(session, tmp_path):
    target = source(session)
    child = session.command("import", path=str(CUBE), units=0.1, parent=target)["entity_id"]
    session.wait(5)
    token, state = assessment(session, target, tetrahedron(tmp_path))
    assert not state["matching_topology"]
    assert state["changes"][0]["target"] == child
    before = session.document
    child_matrix = session.document.entity(child).matrix
    with pytest.raises(ValueError, match="Explicitly approve"):
        session.command("scp.mesh.replace.apply", token=token)
    assert session.document == before
    apply_review(session, token, state)
    assert session.document.entity(child).status == "ready"
    np.testing.assert_allclose(session.document.entity(child).matrix, child_matrix, atol=1e-12)


def apply_review(session, token, state):
    session.command(
        "scp.mesh.replace.apply", token=token, approved=[c["key"] for c in state["changes"]]
    )
    session.wait(10)


def test_stale_mesh_review_rejects_atomically(session):
    target = source(session)
    token, _ = assessment(session, target, CUBE)
    session.command("scp.transform", entity=target, values=[1, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait(5)
    before = session.document
    with pytest.raises(ValueError, match="current successful"):
        session.command("scp.mesh.replace.apply", token=token)
    assert session.document == before


def test_indexed_deformer_removal_is_reviewed_and_control_is_preserved(session, tmp_path):
    target = source(session)
    hook = session.command("control.create", kind="HOOK", entity=target)
    binding = session.command(
        "deformer.add", control=hook, target=dict(owner=target, stage="GEOMETRY"), indices=[0, 1]
    )
    session.wait(5)
    token, state = assessment(session, target, tetrahedron(tmp_path))
    assert any(c["key"] == "deformer:" + binding for c in state["changes"])
    apply_review(session, token, state)
    assert session.document.control(hook).id == hook
    assert not session.document.entity(target).deformers
    session.command("undo")
    assert session.document.entity(target).deformers[0].id == binding


def test_anchor_replacement_uses_shared_capture_and_retains_target(session, tmp_path):
    from tests.test_anchor_operations import scene

    target, _, anchor = scene(session)
    token, state = assessment(session, target, tetrahedron(tmp_path))
    assert any(c["target"] == anchor.id for c in state["changes"])
    apply_review(session, token, state)
    current = session.document.object(anchor.id)
    assert current.binding.reference == anchor.binding.reference
    assert current.result.status == "ready", current.result.error
    np.testing.assert_allclose(current.resolved_position, anchor.resolved_position, atol=1e-10)


def test_fiber_replacement_retains_pin_targets_and_accepted_shape(session, tmp_path):
    from tests.test_fiber_creation import bind
    from tests.test_surface_workflow import curve

    target = source(session)
    fiber = bind(session, target, curve(session, 0))
    original = session.resources.paths[fiber.result.asset].path.array().copy()
    token, state = assessment(session, target, tetrahedron(tmp_path))
    apply_review(session, token, state)
    current = session.document.object(fiber.id)
    assert current.result.status == "ready", current.result.error
    assert [b.reference for b in current.bindings] == [b.reference for b in fiber.bindings]
    actual = session.resources.paths[current.result.asset].path.array()
    np.testing.assert_allclose(actual[:, :3], original[:, :3], atol=1e-8)


def test_rename_and_new_relationships_invalidate_reviews(session):
    target = source(session)
    token, _ = assessment(session, target, CUBE)
    session.command("scp.rename", entity=target, name="Renamed")
    assert session.command("scp.mesh.replace.status")["state"] == "stale"
    with pytest.raises(ValueError, match="definitions changed"):
        session.command("scp.mesh.replace.apply", token=token)
    token, _ = assessment(session, target, CUBE)
    session.command("scp.empty", parent=target, name="New child")
    assert session.command("scp.mesh.replace.status")["state"] == "stale"
    with pytest.raises(ValueError, match="relationships changed"):
        session.command("scp.mesh.replace.apply", token=token)


def test_nonroot_owner_recapture_preserves_pose(session, tmp_path):
    parent = source(session)
    target = session.command("import", path=str(CUBE), units=0.1, parent=parent)["entity_id"]
    session.wait(5)
    before = session.document.entity(target).matrix
    token, state = assessment(session, target, tetrahedron(tmp_path))
    assert any(row["action"] == "OWNER_BINDING" for row in state["changes"])
    apply_review(session, token, state)
    np.testing.assert_allclose(session.document.entity(target).matrix, before, atol=1e-12)


def test_import_units_are_retained_without_extra_prompt(session):
    target = session.command("import", path=str(CUBE), units=0.01, y_up=True)["entity_id"]
    session.wait(5)
    before = session.assets[session.document.entity(target).result.asset].mesh.array(0).copy()
    token, state = assessment(session, target, CUBE)
    apply_review(session, token, state)
    item = session.document.entity(target)
    source_asset = session.assets[item.primitive.source]
    assert source_asset.units == 0.01 and source_asset.y_up
    np.testing.assert_allclose(session.assets[item.result.asset].mesh.array(0), before, atol=1e-14)


def test_failed_assessment_and_cancel_leave_no_authored_change(session, tmp_path):
    target = source(session)
    before, cursor = session.document, session.history.cursor
    broken = tmp_path / "broken.obj"
    broken.write_text("not a mesh")
    session.command("scp.mesh.replace.assess", target=target, path=str(broken))
    session.wait(5)
    assert session.command("scp.mesh.replace.status")["state"] == "failed"
    assert session.document == before and session.history.cursor == cursor
    assessment(session, target, CUBE)
    session.command("scp.mesh.replace.cancel")
    assert session.command("scp.mesh.replace.status")["state"] == "idle"
    assert session.document == before and session.history.cursor == cursor
