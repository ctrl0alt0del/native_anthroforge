"""Formula batches must not swallow intervening pose or geometry calculations."""

from anthroforge.application import dependencies
from tests.test_driving_formulas import curve, driver, reference, result


def configure_chain(session, root, child):
    target = curve(session)
    session.scheduler.can_publish = lambda job: False
    key, first = driver(
        session, root, "value", value=2.0, path=reference(root, ("transform", "scale"), 0)
    )
    _, second = pose_driver(session, target, child)
    session.command(
        "property.set", reference=reference(root, ("transform", "position"), 1), value=1.0
    )
    session.scheduler.can_publish = lambda job: True
    return target, key, first, second


def pose_driver(session, target, child):
    return driver(
        session,
        target,
        "x",
        path=reference(target, ("transform", "position"), 0),
        inputs=[dict(name="x", property=reference(child, ("world_transform", "position"), 0))],
    )


def position(session, target, space="transform"):
    return session.command("property.get", reference=reference(target, (space, "position"), 0))[
        "value"
    ]


def test_drivers_across_attachment_pose_finish_and_read_current_output(session, assembly):
    root, child = assembly
    target, key, first, second = configure_chain(session, root, child)
    assert not dependencies.graph(session.document).blocked
    session.wait(5)
    assert result(session, first).status == result(session, second).status == "ready"
    assert position(session, target) == position(session, child, "world_transform")
    session.command("driver.value", driver=key, value=3.0)
    session.wait(5)
    assert not session.scheduler.errors
    assert position(session, target) == position(session, child, "world_transform")


def test_explicit_manual_drivers_across_pose_are_all_completed(session, assembly):
    root, child = assembly
    target, key, first, second = configure_chain(session, root, child)
    session.wait(5)
    session.command("update_mode", entity=root, mode="MANUAL")
    session.command("update_mode", entity=target, mode="MANUAL")
    session.command("driver.value", driver=key, value=4.0)
    session.command("evaluate", entities=[target])
    session.wait(5)
    assert result(session, first).status == result(session, second).status == "ready"
    assert position(session, target) == position(session, child, "world_transform")
