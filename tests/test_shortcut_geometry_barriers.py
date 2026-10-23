"""Temporary surface overrides must participate in attachment batch planning."""

from tests.conftest import CUBE
from tests.test_shortcut_attachment_edits import reference


def chain(session, parent):
    body = session.command("primitive.create", kind="BODY", parent=parent)
    session.wait(5)
    child = session.command("import", path=str(CUBE), units=0.1, parent=body)["entity_id"]
    session.wait(5)
    session.command("scp.attachment", entity=child, parent_mode="OBJECT_ORIGIN")
    control = session.command("control.create", entity=body)
    session.command("deformer.add", control=control, target=dict(owner=body, stage="GEOMETRY"))
    session.wait(5)
    return body, child, control


def configure(session, parent, body, child, control):
    key = session.command("driver.create", value=0.0)
    for target in (parent, control):
        session.command(
            "driver.formula.add", driver=key, target=reference(target), expression="1+value"
        )
    policy = dict(scope=body, descendants=[dict(target=child, parent_anchor="SURFACE_NEAREST")])
    session.command("driver.configure", driver=key, changes=dict(policy=policy))
    session.wait(5)
    return key


def test_surface_override_waits_for_parent_geometry_without_pose_batch_deadlock(session, assembly):
    body, child, control = chain(session, assembly[1])
    key = configure(session, assembly[1], body, child, control)
    original = session.document.entity(child).attachment
    session.command("driver.value", driver=key, value=0.1)
    session.wait(2)
    assert not session.scheduler.errors
    assert session.document.entity(child).attachment == original
    assert session.document.entity(child).pose_receipt.effective.parent_mode == "SURFACE_NEAREST"
    assert not session.document.shortcut_edits
