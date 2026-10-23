"""Shortcut transforms resolve retained anatomy; direct transforms still recapture."""

import pytest

from tests.conftest import CUBE
from tests.test_shortcut_attachment_edits import reference, retained_anchor


def edit(session, child, value):
    session.command("shortcut.set", reference=reference(child), value=value)


def assert_retained(session, original, anchor):
    session.wait(5)
    assert not session.scheduler.errors
    assert session.document.entity(original.id).attachment == original.attachment
    assert retained_anchor(session, original.id) == pytest.approx(anchor, abs=1e-12)


@pytest.mark.parametrize("mode", ["LIVE", "ON_RELEASE", "MANUAL"])
def test_default_shortcut_keeps_binding_without_backsolve(session, assembly, mode):
    _, child = assembly
    original, anchor = session.document.entity(child), retained_anchor(session, child)
    session.command("update_mode", entity=child, mode=mode)
    edit(session, child, 2.0)
    if mode == "MANUAL":
        session.command("evaluate", entities=[child])
    assert_retained(session, original, anchor)
    assert session.command("property.get", reference=reference(child))["value"] == 2.0
    assert not session.document.shortcut_edits


def test_rapid_drag_pause_and_cancel_keep_one_original_binding(session, assembly):
    _, child = assembly
    original, anchor = session.document.entity(child), retained_anchor(session, child)
    session.begin()
    for size in (1.2, 1.5, 2.0):
        edit(session, child, size)
    assert_retained(session, original, anchor)
    edit(session, child, 3.0)
    assert_retained(session, original, anchor)
    session.cancel()
    session.wait(5)
    assert session.document.entity(child).matrix == original.matrix
    assert not session.document.shortcut_edits


def test_undo_redo_restores_retained_binding_and_resolved_pose(session, assembly):
    _, child = assembly
    original, anchor = session.document.entity(child), retained_anchor(session, child)
    edit(session, child, 2.0)
    assert_retained(session, original, anchor)
    accepted = session.document.entity(child).matrix
    session.command("undo")
    session.wait(5)
    assert session.document.entity(child).matrix == original.matrix
    session.command("redo")
    assert_retained(session, original, anchor)
    assert session.document.entity(child).matrix == accepted


def test_manual_retention_survives_save_and_reopen(session, assembly, tmp_path):
    _, child = assembly
    original, anchor = session.document.entity(child), retained_anchor(session, child)
    session.command("update_mode", entity=child, mode="MANUAL")
    edit(session, child, 2.0)
    path = str(tmp_path / "pending-shortcut.anthroforge")
    session.command("save", path=path, blocked_policy="wait")
    session.command("open", path=path)
    session.wait(5)
    session.command("evaluate", entities=[child])
    assert_retained(session, original, anchor)


@pytest.mark.parametrize("operation", ["property.set", "scp.transform"])
def test_direct_edit_supersedes_pending_shortcut_retention(session, assembly, operation):
    _, child = assembly
    original = session.document.entity(child).attachment
    session.command("update_mode", entity=child, mode="MANUAL")
    edit(session, child, 2.0)
    if operation == "property.set":
        session.command(operation, reference=reference(child), value=3.0)
    else:
        session.command(operation, entity=child, values=[1, 0, 0, 0, 0, 0, 3, 1, 1])
    session.command("evaluate", entities=[child])
    session.wait(5)
    assert not session.scheduler.errors
    assert session.document.entity(child).attachment != original
    assert not session.document.shortcut_edits


def driven_pair(session, root, child):
    other = session.command("import", path=str(CUBE), units=0.3, parent=root)["entity_id"]
    session.wait(5)
    key = session.command("driver.create", value=1.0)
    for target in (child, other):
        session.command(
            "driver.formula.add", driver=key, target=reference(target), expression="value"
        )
    session.wait(5)
    return key, other


def test_multi_owner_driver_keeps_bindings_without_inventing_policy_scope(session, assembly):
    root, child = assembly
    key, other = driven_pair(session, root, child)
    originals = [session.document.entity(k) for k in (child, other)]
    anchors = [retained_anchor(session, k) for k in (child, other)]
    assert session.command("driver.inspect", driver=key)["scp_owner"] == ""
    session.command("driver.value", driver=key, value=2.0)
    for original, anchor in zip(originals, anchors, strict=True):
        assert_retained(session, original, anchor)
    assert not session.document.shortcut_edits
