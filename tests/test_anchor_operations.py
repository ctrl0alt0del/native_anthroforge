"""Attached points share capture, scheduling, history and retention semantics with anatomy."""

from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.points import Anchor, Point

CUBE = Path(__file__).resolve().parents[1] / "examples/primitives/cube.obj"


def scene(session):
    parent = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait()
    point = session.command("construction.point.create", position=[0, 0, 0.7])
    original = session.document.object(point)
    anchor = session.command("anchor.create", source=point, parent=parent)["object_id"]
    session.wait()
    assert anchor in session.document.registry.records, [j.error for j in session.scheduler.jobs]
    return parent, original, session.document.object(anchor)


def test_point_only_document_edit_undo_and_native_position(session):
    key = session.command("construction.point.create", position=[1, 2, 3])
    assert isinstance(session.document.object(key), Point) and not session.document.entities
    session.command("construction.point.update", target=key, position=[3, 2, 1])
    assert session.document.object(key).position == (3, 2, 1)
    session.navigate(-1)
    assert session.document.object(key).position == (1, 2, 3)


def test_anchor_is_independent_point_with_retained_binding_and_one_undo(session):
    parent, original, anchor = scene(session)
    assert isinstance(anchor, Anchor) and isinstance(anchor, Point)
    assert anchor.id != original.id and session.document.object(original.id) == original
    np.testing.assert_allclose(anchor.resolved_position, [0, 0, 0.7])
    session.navigate(-1)
    assert anchor.id not in session.document.registry.records
    session.navigate(1)
    session.wait()
    assert session.document.object(anchor.id).binding == anchor.binding


def test_parent_motion_updates_anchor_without_nearest_rebind(session):
    parent, original, anchor = scene(session)
    session.command("scp.transform", entity=parent, values=[0, 0, 2, 0, 0, 0, 1, 1, 1])
    session.wait()
    moved = session.document.object(anchor.id)
    assert moved.result.status == "ready", moved.result.error
    assert moved.binding == anchor.binding and moved.result.revision > anchor.result.revision
    np.testing.assert_allclose(moved.resolved_position, [0, 0, 2.7])
    assert session.document.object(original.id) == original


def test_anchor_rebind_is_explicit_and_undoable(session):
    parent, _, anchor = scene(session)
    session.command("anchor.rebind", target=anchor.id, parent=parent, position=[1, 0, 0.7])
    session.wait()
    moved = session.document.object(anchor.id)
    assert moved.binding != anchor.binding, [j.error for j in session.scheduler.jobs]
    np.testing.assert_allclose(moved.resolved_position, [1, 0, 0.7])
    session.navigate(-1)
    np.testing.assert_allclose(
        session.document.object(anchor.id).resolved_position, anchor.resolved_position
    )


def test_anchor_prevents_target_deletion_and_transform_bypass(session):
    parent, _, anchor = scene(session)
    with pytest.raises(ValueError, match="Rebind"):
        session.command("scp.delete", entity=parent)
    with pytest.raises(ValueError, match="Anchor"):
        session.command("object.transform", target=anchor.id, values=[1, 0, 0, 0, 0, 0, 1, 1, 1])
    session.command("object.delete", target=anchor.id)
    session.command("scp.delete", entity=parent)
    assert not session.document.entities


def test_anchor_roundtrip_preserves_capture_and_startup_does_not_rebind(session, tmp_path):
    parent, _, anchor = scene(session)
    path = tmp_path / "anchor.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    session.wait()
    session.command("open", path=str(path))
    session.wait()
    loaded = session.document.object(anchor.id)
    assert loaded.binding == anchor.binding and loaded.resolved_frame == anchor.resolved_frame
    session.command("scp.transform", entity=parent, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(session.document.object(anchor.id).resolved_position, [0, 0, 1.7])
