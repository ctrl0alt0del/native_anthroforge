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


def test_parent_scale_can_depend_on_attached_child_volume_without_false_cycle(session, assembly):
    root, child = assembly
    ref = reference(child, ("world_transform", "volume_scale"))
    volume = value(session, ref)
    formula = scale_driver(session, root, ref, "size*2")
    session.wait(5)
    assert result(session, formula).status == "ready"
    assert value(session, ref) == volume
    session.command(
        "property.set", reference=reference(child, ("transform", "scale"), 0), value=0.5
    )
    session.wait(5)
    assert value(session, reference(root, ("transform", "scale"), 0)) == value(session, ref) * 2


def test_volume_dependency_retains_own_scale_writer_cycle(session, assembly):
    root, child = assembly
    ref = reference(child, ("world_transform", "volume_scale"))
    first = scale_driver(session, root, ref)
    second = scale_driver(session, child, reference(root, ("transform", "scale"), 0))
    session.wait(5)
    assert result(session, first).status == result(session, second).status == "failed"


def scale_driver(session, target, source, expression="size"):
    return driver(
        session,
        target,
        expression,
        path=reference(target, ("transform", "scale"), 0),
        inputs=[dict(name="size", property=source)],
    )[1]


def value(session, ref):
    return session.command("property.get", reference=ref)["value"]
