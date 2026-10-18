"""Observable source sharing, placement, reference safety and transaction contracts."""

import numpy as np
import pytest

from anthroforge.application.curve_sources import world


def assembly(session):
    root = session.command("scp.empty", name="Assembly")
    curve = session.command("curve.create")
    first = session.command("primitive.from_curves", curves=[curve], kind="BODY", parent=root)
    second = session.command("primitive.from_curves", curves=[curve], kind="BODY", parent=root)
    session.wait(5)
    return root, curve, first, second


def vertices(session, entity):
    return session.assets[session.document.entity(entity).asset].mesh.array(0).copy()


def move(session, target, x, operation="object.transform"):
    key = "entity" if operation == "scp.transform" else "target"
    session.command(operation, **{key: target}, values=[x, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait(5)


def test_curve_creation_has_no_anatomical_wrapper_and_one_undo(session):
    before = session.history.cursor
    curve = session.command("curve.create", name="Guide")
    assert not session.document.entities
    assert session.document.object(curve).name == "Guide"
    assert session.history.cursor == before + 1
    session.command("undo")
    assert not session.document.objects
    session.command("redo")
    assert session.document.object(curve).name == "Guide"


def test_shared_source_edit_updates_both_consumers(session):
    _, curve, first, second = assembly(session)
    before = vertices(session, first)
    point = session.document.object(curve).points[0].id
    session.command("curve.point.update", curve=curve, point=point, position=[-0.5, 0.2, 0])
    session.wait(5)
    assert not np.allclose(vertices(session, first), before)
    np.testing.assert_allclose(vertices(session, first), vertices(session, second))
    assert len(session.document.objects) == 1
    assert not session.scheduler.errors


def test_consumer_move_does_not_move_source_or_other_consumer(session):
    _, curve, first, second = assembly(session)
    source, before = session.document.object(curve), vertices(session, second)
    move(session, first, 2, "scp.transform")
    assert session.document.object(curve) is source
    np.testing.assert_allclose(vertices(session, second), before)
    assert session.document.entity(first).matrix[3] == pytest.approx(2)


def test_shape_only_mode_preserves_result_and_ignores_source_pose(session):
    _, curve, first, second = assembly(session)
    move(session, curve, 0.3)
    before = vertices(session, first)
    session.command("primitive.curve_mode", entity=first, curve=curve, mode="SHAPE_ONLY")
    session.wait(5)
    np.testing.assert_allclose(vertices(session, first), before)
    move(session, curve, 0.8)
    np.testing.assert_allclose(vertices(session, first), before)
    assert not np.allclose(vertices(session, second), before)


def test_switching_back_to_transform_mode_has_no_jump(session):
    _, curve, first, _ = assembly(session)
    session.command("primitive.curve_mode", entity=first, curve=curve, mode="SHAPE_ONLY")
    session.wait(5)
    move(session, curve, 0.6)
    before = vertices(session, first)
    session.command("primitive.curve_mode", entity=first, curve=curve, mode="SHAPE_AND_TRANSFORM")
    session.wait(5)
    np.testing.assert_allclose(vertices(session, first), before)
    move(session, curve, 0.8)
    np.testing.assert_allclose(vertices(session, first), before + [0.2, 0, 0], atol=1e-12)


def test_referenced_curve_deletion_lists_consumers(session):
    _, curve, first, second = assembly(session)
    before = session.document
    with pytest.raises(ValueError, match="referenced by consumers") as error:
        session.command("object.delete", target=curve)
    assert first in str(error.value) and second in str(error.value)
    assert session.document == before


def test_deleting_last_consumer_preserves_unassigned_source(session):
    curve = session.command("curve.create")
    body = session.command("primitive.from_curves", curves=[curve], kind="BODY")
    session.wait(5)
    session.command("scp.delete", entity=body)
    assert session.document.object(curve)
    assert not session.document.entities
    session.command("object.delete", target=curve)
    assert not session.document.objects


def test_deleting_owned_primitive_promotes_curve_without_moving_it(session):
    body = session.command("primitive.create", kind="BODY")
    session.wait(5)
    curve = session.document.entity(body).primitive.curves[0].id
    move(session, body, 0.7, "scp.transform")
    before = world(session.engine, session.document, curve)
    session.command("scp.delete", entity=body)
    assert not session.document.object(curve).parent
    np.testing.assert_allclose(world(session.engine, session.document, curve), before)


def test_shared_sampling_lock_identifies_attached_consumer(session):
    _, curve, first, second = assembly(session)
    child = session.command("scp.empty", name="Child", parent=first)
    session.wait(5)
    with pytest.raises(ValueError, match=child):
        session.command("curve.edit", curve=curve, resolution=32)
    session.command("scp.delete", entity=child)
    session.command("curve.edit", curve=curve, resolution=32)
    session.wait(5)
    assert session.document.object(curve).resolution == 32
    assert session.document.entity(second).result.status == "ready"


def test_shared_curve_roundtrip_and_edit_undo(session, tmp_path):
    _, curve, first, second = assembly(session)
    path = str(tmp_path / "shared.anthroforge")
    session.command("save", path=path, blocked_policy="wait")
    session.command("open", path=path)
    assert session.document.entity(first).primitive.curves[0].id == curve
    assert session.document.entity(second).primitive.curves[0].id == curve
    before = session.document.object(curve)
    session.command(
        "curve.point.update", curve=curve, point=before.points[0].id, position=[0, 1, 0]
    )
    session.wait(5)
    session.command("undo")
    assert session.document.object(curve) == before


def test_rename_does_not_schedule_geometry(session):
    _, curve, _, _ = assembly(session)
    jobs = len(session.scheduler.jobs)
    session.command("object.rename", target=curve, name="Guide")
    assert len(session.scheduler.jobs) == jobs
    assert session.command("object.inspect", target=curve)["state"]["name"] == "Guide"


def test_make_independent_preserves_shape_then_disconnects_edits(session):
    _, curve, first, second = assembly(session)
    before = vertices(session, first)
    copied = session.command("primitive.make_independent", entity=first, curve=curve)
    session.wait(5)
    np.testing.assert_allclose(vertices(session, first), before)
    assert copied != curve
    original_ids = {p.id for p in session.document.object(curve).points}
    assert not original_ids.intersection(p.id for p in session.document.object(copied).points)
    move(session, curve, 0.4)
    np.testing.assert_allclose(vertices(session, first), before)
    assert not np.allclose(vertices(session, second), before)


def test_parented_shared_source_does_not_apply_parent_pose_twice(session):
    root, curve, first, second = assembly(session)
    session.command("object.reparent", target=curve, parent=root)
    session.wait(5)
    before = vertices(session, first)
    move(session, root, 0.5, "scp.transform")
    assert session.document.entity(first).matrix[3] == pytest.approx(0.5)
    assert session.document.entity(second).matrix[3] == pytest.approx(0.5)
    np.testing.assert_allclose(vertices(session, first), before)
