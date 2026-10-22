"""Wrapper-only attachment policies span gestures and coordinated calculations."""

from math import pi

import pytest

from anthroforge.application import storage
from anthroforge.native.shortcut_attachments import capture


def reference(target, field="scale", component=0):
    return dict(target=target, path=["transform", field], component=component)


def retained_anchor(session, child):
    item = session.document.entity(child)
    meshes = {k: v.mesh for k, v in session.assets.items()}
    return capture(session.engine, item, session.document.entity(item.parent), meshes)[3]


def configure(session, ref, **policy):
    session.command("shortcut.configure", reference=ref, policy=policy)


def test_backsolve_preserves_owner_anchor_and_authored_binding(session, assembly):
    _, child = assembly
    ref, original = reference(child), session.document.entity(child)
    configure(session, ref, backsolve=True)
    anchor = retained_anchor(session, child)
    session.command("shortcut.set", reference=ref, value=2.0)
    session.wait(5)
    assert not session.scheduler.errors
    assert retained_anchor(session, child) == pytest.approx(anchor)
    assert session.document.entity(child).attachment == original.attachment
    assert session.command("property.get", reference=ref)["value"] == 2.0
    assert not session.document.shortcut_edits
    session.command("undo")
    assert session.document.entity(child).matrix == original.matrix


def test_ordinary_property_does_not_apply_wrapper_backsolve(session, assembly):
    _, child = assembly
    ref, anchor = reference(child), retained_anchor(session, child)
    configure(session, ref, backsolve=True)
    session.command("property.set", reference=ref, value=2.0)
    session.wait(5)
    assert retained_anchor(session, child) != pytest.approx(anchor)
    assert not session.document.shortcut_edits


def test_follow_override_keeps_authored_settings_and_survives_roundtrip(session, assembly):
    root, child = assembly
    original, ref = session.document.entity(child), reference(root, "rotation", 2)
    configure(session, ref, descendants=[dict(target=child, follow_rotation="DISABLED")])
    session.command("shortcut.set", reference=ref, value=pi / 3)
    session.wait(5)
    current = session.document.entity(child)
    assert not session.scheduler.errors
    assert current.attachment == original.attachment
    assert current.matrix[:3] == pytest.approx(original.matrix[:3])
    assert current.pose_receipt.effective.follow_rotation is False
    assert storage.decode_document(storage.document_state(session.document)) == session.document
    assert not session.document.shortcut_edits


def test_paused_drag_reuses_binding_and_cancel_restores_pose(session, assembly):
    _, child = assembly
    ref, original = reference(child), session.document.entity(child)
    configure(session, ref, backsolve=True)
    session.begin()
    session.command("shortcut.set", reference=ref, value=1.5)
    session.wait(5)
    context = session.document.shortcut_edits[0]
    session.command("shortcut.set", reference=ref, value=3.0)
    session.wait(5)
    assert session.document.shortcut_edits == (context,)
    assert retained_anchor(session, child) == pytest.approx(context.anchor.parent_local)
    session.cancel()
    session.wait(5)
    assert session.document.entity(child).matrix == original.matrix


def body(session, root):
    key = session.command("primitive.create", kind="BODY", parent=root)
    session.wait(5)
    session.command("scp.attachment", entity=key, child_mode="FACE_CENTER")
    session.wait(5)
    piece = session.document.entity(key).primitive.pieces[0]
    ref = dict(target=key, path=["primitive", "pieces", "@" + piece.id, "width"])
    configure(session, ref, backsolve=True)
    return key, ref


def test_geometry_publication_backsolves_before_finishing(session, assembly):
    key, ref = body(session, assembly[0])
    anchor = retained_anchor(session, key)
    session.command("shortcut.set", reference=ref, value=0.4)
    session.wait(5)
    assert not session.scheduler.errors
    assert retained_anchor(session, key) == pytest.approx(anchor)
    assert session.command("property.get", reference=ref)["value"] == 0.4
    assert not session.document.shortcut_edits


def test_manual_geometry_keeps_context_through_save(session, assembly, tmp_path):
    key, ref = body(session, assembly[0])
    anchor = retained_anchor(session, key)
    session.command("update_mode", entity=key, mode="MANUAL")
    session.command("shortcut.set", reference=ref, value=0.4)
    session.wait(5)
    assert session.document.shortcut_edits
    path = str(tmp_path / "manual.anthroforge")
    session.command("save", path=path, blocked_policy="wait")
    session.command("open", path=path)
    session.wait(5)
    session.command("evaluate", entities=[key])
    session.wait(5)
    assert not session.scheduler.errors
    assert retained_anchor(session, key) == pytest.approx(anchor)
