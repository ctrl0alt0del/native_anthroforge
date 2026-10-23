"""Multi-owner controls retain explicit attachment scope without changing ownership."""

from dataclasses import asdict
from math import pi

import pytest

from anthroforge.application import shortcut_copies, storage
from tests.test_shortcut_attachment_edits import reference


def driver(session, root, child):
    key = session.command("driver.create", value=0.0, dimension="ANGLE")
    session.command(
        "driver.formula.add", driver=key, target=reference(root, "rotation", 2), expression="value"
    )
    session.command(
        "driver.formula.add", driver=key, target=reference(child, "scale"), expression="1+value/rad"
    )
    session.wait(5)
    return key


def test_explicit_scope_retains_multi_owner_presentation_and_descendant_binding(session, assembly):
    root, child = assembly
    key = driver(session, root, child)
    original = session.document.entity(child).attachment
    policy = dict(scope=root, descendants=[dict(target=child, follow_rotation="DISABLED")])
    session.command("driver.configure", driver=key, changes=dict(policy=policy))
    session.command("driver.value", driver=key, value=pi / 6)
    session.wait(5)
    assert not session.scheduler.errors
    info = session.command("driver.inspect", driver=key)
    assert info["scp_owner"] == "" and set(info["owners"]) == {root, child}
    assert session.document.entity(child).attachment == original
    assert session.document.entity(child).pose_receipt.effective.follow_rotation is False
    assert storage.decode_document(storage.document_state(session.document)) == session.document


def test_scope_rejects_uncontrolled_object_and_remaps_on_copy(session, assembly):
    root, child = assembly
    key = driver(session, root, child)
    with pytest.raises(ValueError, match="controlled SCPs"):
        session.command("driver.configure", driver=key, changes=dict(policy=dict(scope="missing")))
    session.command("driver.configure", driver=key, changes=dict(policy=dict(scope=root)))
    policy = next(d.policy for d in session.document.driving_shortcuts if d.id == key)
    assert asdict(shortcut_copies.policy(policy, {root: "copy"}))["scope"] == "copy"
