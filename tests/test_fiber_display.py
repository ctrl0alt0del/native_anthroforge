"""Radius publication and exact picking share one displayed native mesh revision."""

from tests.test_quick_fiber import cube
from tests.test_quick_fiber_interaction import controller as controller


def frames(controller):
    for _ in range(8):
        for model in controller.geometry_models():
            model.drain()
        controller.frame_presented()


def setup(controller):
    target = cube(controller.session)
    create_fiber(controller, target)
    controller.session.wait(5)
    controller.refresh()
    controller.session.wait(5)
    frames(controller)
    assert controller.fiber_display.model.active_rows()
    return controller.session.document.objects[0].id


def create_fiber(controller, target):
    controller.run(
        "fiber.place",
        dict(
            points=[
                dict(position=[-0.4, 0, 0.501], target=target),
                dict(position=[0.4, 0, 0.501], target=target),
            ]
        ),
    )


def radius(controller, key, value):
    controller.run("fiber.presentation", dict(target=key, radius=value))


def test_display_replacement_retains_geometry_and_switches_picking_at_frame_boundary(controller):
    key = setup(controller)
    display, before = controller.fiber_display, controller.session.document.objects
    old = display.model.active_rows()[0]["handle"]
    assert not display.hits([0, 0.015, 3], [0, 0, -1])
    radius(controller, key, 0.02)
    assert display.model.active_rows()[0]["handle"] == old
    controller.session.wait(5)
    assert display.model.active_rows()[0]["handle"] == old
    assert not display.hits([0, 0.015, 3], [0, 0, -1])
    frames(controller)
    assert display.model.active_rows()[0]["handle"] != old
    assert display.hits([0, 0.015, 3], [0, 0, -1])[0]["id"] == key
    assert controller.session.document.objects == before


def test_superseding_radius_hiding_and_zero_radius_release_cached_tubes(controller):
    key = setup(controller)
    radius(controller, key, 0.02)
    radius(controller, key, 0.03)
    radius(controller, key, 0.04)
    controller.session.wait(5)
    frames(controller)
    display = controller.fiber_display
    assert display.model.active_rows()[0]["content"]["radius"] == 0.04
    assert not display.jobs and not controller.session.scheduler.errors
    radius(controller, key, 0)
    frames(controller)
    assert not display.accepted and not display.model.leases
    assert not display.model.active_rows()
