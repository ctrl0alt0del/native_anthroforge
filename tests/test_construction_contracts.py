"""End-to-end construction contracts: dependency failures, history and persistence."""

import numpy as np
import pytest

from anthroforge.application.control_frames import display_frame
from anthroforge.application.geometry_ownership import collect
from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.native import curve_editing
from tests.test_fiber_creation import bind


def create(session, parent="", kind="LOFT"):
    key = session.command("primitive.create", kind=kind, parent=parent)
    session.command("wait", timeout=5)
    return key


def mesh(session, entity):
    return session.assets[session.document.entity(entity).asset].mesh


def move_control(session, control, z):
    session.command("control.transform", control=control, values=[0, 0, z, 0, 0, 0, 1, 1, 1])


def hook(session, entity, control=""):
    control = control or session.command("control.create", entity=entity)
    session.command("deformer.add", control=control, target={"owner": entity})
    session.command("wait", timeout=5)
    return control


def test_zero_weight_shell_roundtrips_canonical_triangles(session, tmp_path):
    entity = create(session)
    weights = [0] * mesh(session, entity).counts[0]
    session.command("thickness.update", entity=entity, weights=weights)
    session.command("wait", timeout=5)
    triangles = mesh(session, entity).array(3).copy()
    vertices = mesh(session, entity).array(0).copy()
    path = str(tmp_path / "collapsed.aforge")
    session.command("save", path=path, blocked_policy="wait")
    session.command("open", path=path)
    np.testing.assert_array_equal(mesh(session, entity).array(3), triangles)
    np.testing.assert_array_equal(mesh(session, entity).array(0), vertices)


def test_shape_edits_preserve_triangle_identity(session):
    entity = create(session)
    before = mesh(session, entity).array(3).copy()
    curve = session.document.object(session.document.entity(entity).primitive.curves[0].id)
    session.command(
        "point.update",
        entity=entity,
        curve=curve.id,
        point=curve.points[0].id,
        position=[-0.4, -0.1, 0.2],
    )
    session.command("wait", timeout=5)
    np.testing.assert_array_equal(mesh(session, entity).array(3), before)


def test_point_translation_preserves_free_handle_offsets(session):
    point = CurvePoint(
        position=(1, 2, 3), left=(0, 2, 3), right=(2, 2, 3), left_mode="FREE", right_mode="FREE"
    )
    curve = Curve((point, CurvePoint(position=(4, 2, 3))))
    moved = curve_editing.point(session.engine, curve, 0, {"position": (2, 3, 4)})
    assert moved.left == (1, 3, 4) and moved.right == (3, 3, 4)


def test_aligned_handle_edit_moves_opposite_handle(session):
    point = CurvePoint(left=(-1, 0, 0), right=(2, 0, 0), left_mode="ALIGNED", right_mode="ALIGNED")
    curve = Curve((point, CurvePoint(position=(4, 0, 0))))
    changed = curve_editing.point(session.engine, curve, 0, {"left": (0, 1, 0)})
    np.testing.assert_allclose(changed.right, [0, -2, 0])


def test_fiber_binding_locks_then_unlocks_topology(session):
    entity = create(session)
    source = session.document.entity(entity).primitive.curves[0].id
    fiber = bind(session, entity, source)
    with pytest.raises(ValueError, match="Topology is locked"):
        session.command("primitive.update", entity=entity, samples=40)
    session.command("object.delete", target=fiber.id)
    session.command("primitive.update", entity=entity, samples=40)
    session.command("wait", timeout=5)
    assert mesh(session, entity).counts[0] == 80


def test_cycle_finishes_preserves_result_and_can_be_broken(session):
    entity = create(session)
    control = hook(session, entity)
    previous = mesh(session, entity)
    session.command("control.follow", control=control, entity=control)
    session.command("wait", timeout=5)
    assert not session.scheduler.blocked
    assert session.document.entity(entity).result.status == "failed"
    assert mesh(session, entity) is previous
    session.command("control.delete", control=control)
    session.command("wait", timeout=5)
    assert session.document.entity(entity).result.status == "ready"


def test_control_cycle_can_be_removed_and_unrelated_geometry_runs(session):
    entity = create(session)
    a, b = hook(session, entity), session.command("control.create", entity=entity)
    session.command("control.follow", control=a, entity=b)
    session.command("control.follow", control=b, entity=a)
    other = create(session, entity)
    assert mesh(session, other).counts[0] > 0
    session.command("control.delete", control=b)
    session.command("wait", timeout=5)
    assert session.document.entity(entity).result.status == "ready"


def test_scp_deletion_detaches_control_in_world_frame(session):
    root = session.command("scp.empty", name="Group")
    entity = create(session, root)
    control = hook(session, entity)
    move_control(session, control, 0.3)
    session.command("wait", timeout=5)
    before = display_frame(session, session.document.control(control))
    session.command("scp.delete", entity=entity)
    item = session.document.control(control)
    assert not item.follow and not item.owners
    np.testing.assert_allclose(item.matrix, before)


def test_shared_hook_respects_manual_and_live_targets(session):
    a = create(session)
    b = create(session, a)
    control = hook(session, a)
    hook(session, b, control)
    session.command("update_mode", entity=b, mode="MANUAL")
    previous = mesh(session, b)
    move_control(session, control, 0.3)
    session.command("wait", timeout=5)
    assert mesh(session, b) is previous
    assert session.document.entity(b).result.status == "pending"
    assert mesh(session, a).bounds[5] == pytest.approx(0.3)


def test_drag_intermediates_are_collected_after_history_commit(session):
    entity = create(session)
    control = hook(session, entity)
    baseline = len(session.assets)
    session.command("begin")
    for z in range(5):
        move_control(session, control, z * 0.01)
        session.command("wait", timeout=5)
    session.command("commit")
    collect(session)
    assert len(session.assets) <= baseline + 1


def test_duplicate_remaps_internal_sharing_once(session):
    a = create(session)
    b = create(session, a)
    control = hook(session, a)
    hook(session, b, control)
    copied = session.command("scp.duplicate", entity=a)
    session.command("wait", timeout=5)
    first = session.document.entity(copied)
    child = next(e for e in session.document.entities if e.parent == copied)
    assert first.deformers[0].control == child.deformers[0].control != control


def test_retired_control_attachment_operation_rejects_without_mutation(session):
    entity = create(session)
    control = hook(session, entity)
    before = session.document
    with pytest.raises(ValueError, match="Unknown"):
        session.command("control.attach", control=control, support=entity)
    assert session.document is before


def surface_consumer(session):
    parent = create(session)
    source = session.document.entity(parent).primitive.curves[0].id
    fiber = bind(session, parent, source)
    child = session.command("primitive.from_curves", curves=[fiber.id], kind="BODY", parent=parent)
    session.command("wait", timeout=5)
    return parent, child


def test_live_consumer_uses_and_reports_pending_manual_input(session):
    parent, child = surface_consumer(session)
    session.command("update_mode", entity=parent, mode="MANUAL")
    source = mesh(session, parent)
    lift_first_point(session, parent)
    session.command("wait", timeout=5)
    assert mesh(session, parent) is source
    assert parent in session.document.entity(child).result.pending
    session.command("evaluate", entities=[parent])
    session.command("wait", timeout=5)
    assert not session.document.entity(child).result.pending
    assert not session.scheduler.blocked


def lift_first_point(session, entity):
    curve = session.document.object(session.document.entity(entity).primitive.curves[0].id)
    session.command(
        "point.update",
        entity=entity,
        curve=curve.id,
        point=curve.points[0].id,
        position=[-0.5, -0.15, 0.2],
    )


def test_pose_following_worker_does_not_wait_for_its_geometry_consumer(session):
    from anthroforge.application.task_schedulers import MeasuredTaskScheduler

    entity = create(session)
    control = hook(session, entity)
    session.scheduler.task_schedulers["control_pose"] = MeasuredTaskScheduler()
    move_control(session, control, 0.4)
    session.command("wait", timeout=3)
    assert mesh(session, entity).bounds[5] == pytest.approx(0.4)
    assert not session.scheduler.errors


def test_geometry_publication_does_not_change_pose_read_revision(session):
    from anthroforge.application.construction_policy import revisions
    from anthroforge.core.results import Port

    entity = create(session)
    ports = {Port(entity, "pose")}
    before = revisions(session.document, ports)
    lift_first_point(session, entity)
    session.command("wait", timeout=5)
    assert revisions(session.document, ports) == before
    session.command("scp.transform", entity=entity, values=[1, 0, 0, 0, 0, 0, 1, 1, 1])
    assert revisions(session.document, ports) != before


def weighted_curve_hook(session, entity):
    curve = session.document.object(session.document.entity(entity).primitive.curves[0].id)
    control = session.command("control.create", entity=entity)
    binding = session.command(
        "deformer.add",
        control=control,
        target=dict(owner=entity, stage="CURVE", component=curve.id),
        indices=[1],
        weights=[0, 0.7, 0, 0, 0, 0],
    )
    return curve, binding


def test_curve_insertion_preserves_membership_and_weight_identity(session):
    from anthroforge.application.deformer_operations import locate
    from anthroforge.application.membership import resolve

    entity = create(session)
    curve, binding = weighted_curve_hook(session, entity)
    insert_first_point(session, entity, curve.id)
    current = session.document.object(session.document.entity(entity).primitive.curves[0].id)
    resolved = resolve(locate(session, binding), current)
    assert resolved.indices == (4,)
    assert resolved.weights[4] == 0.7 and sum(resolved.weights) == 0.7
    session.command("wait", timeout=5)
    assert session.document.entity(entity).result.status == "ready"


def insert_first_point(session, entity, curve):
    session.command(
        "point.insert", entity=entity, curve=curve, index=0, point=dict(position=[-0.8, -0.15, 0])
    )


def test_switch_manual_pending_construction_to_live_evaluates(session):
    entity = create(session)
    session.command("update_mode", entity=entity, mode="MANUAL")
    lift_first_point(session, entity)
    assert session.document.entity(entity).result.status == "pending"
    session.command("update_mode", entity=entity, mode="LIVE")
    session.command("wait", timeout=5)
    assert session.document.entity(entity).result.status == "ready"
    assert mesh(session, entity).bounds[5] == pytest.approx(0.2)


def test_new_primitives_remain_editable_in_focused_workspace(session):
    entity = create(session)
    session.command("workspace.create", name="Part", members=[entity])
    child = create(session, entity, "BODY")
    session.command("primitive.update", entity=child, samples=40)
    assert child in session.workspace.members


def test_removing_bound_body_curve_rejects_orphaned_base_binding(session):
    entity = create(session, kind="BODY")
    session.command("curve.add", entity=entity)
    primitive = session.document.entity(entity).primitive
    control = session.command("control.create", entity=entity)
    session.command(
        "deformer.add",
        control=control,
        target=dict(owner=entity, stage="BASE", component=primitive.pieces[0].id),
    )
    with pytest.raises(ValueError, match="bindings first"):
        session.command("curve.remove", entity=entity, curve=primitive.curves[0].id)


def test_deleted_support_detaches_and_recalculates_external_consumers(session):
    root = session.command("scp.empty", name="Group")
    support, target = create(session, root), create(session, root)
    control = session.command("control.create", entity=support)
    hook(session, target, control)
    session.command("scp.delete", entity=support)
    session.command("wait", timeout=5)
    assert session.document.entity(target).result.status == "ready"
    assert session.document.control(control).result.status == "ready"
