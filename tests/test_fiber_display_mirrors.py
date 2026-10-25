"""World-radius presentation shares accepted tube geometry with strict reflected instances."""

from anthroforge.core.mirroring import MirrorInstance
from tests.test_fiber_display import frames, radius
from tests.test_mirroring_desktop import controller as controller
from tests.test_mirroring_desktop import mirrored_cube


def setup(controller):
    root, target, _ = mirrored_cube(controller)
    controller.run(
        "fiber.place",
        dict(
            owner=target, points=[dict(position=[x, 0, 0.501], target=target) for x in (-0.4, 0.4)]
        ),
    )
    controller.session.wait(5)
    controller.refresh()
    controller.session.wait(5)
    frames(controller)
    key = controller.session.document.objects[0].id
    return root, key, MirrorInstance(key, root).id


def rows(controller):
    return {r["id"]: r for r in controller.fiber_display.model.active_rows()}


def test_mirror_tubes_share_source_geometry_and_pick_reflected_position(controller):
    _, key, mirror = setup(controller)
    displayed = rows(controller)
    assert displayed[key]["handle"] == displayed[mirror]["handle"]
    assert displayed[mirror]["readonly"] and not displayed[mirror]["context_dimmed"]
    assert len(controller.fiber_display.accepted) == 1
    assert controller.fiber_display.hits([4, 0, 3], [0, 0, -1])[0]["id"] == mirror
    assert not controller.path_model.active_rows()
    controller.select(mirror)
    assert controller.selectedData["readonly"]


def test_mirror_only_and_hidden_source_keep_shared_radius_result(controller):
    _, key, mirror = setup(controller)
    handle = rows(controller)[key]["handle"]
    controller.run("workspace.update", dict(mirror_display="MIRROR", hidden=[key]))
    frames(controller)
    displayed = rows(controller)
    assert not displayed[key]["visible"] and displayed[mirror]["visible"]
    assert displayed[mirror]["handle"] == handle
    assert controller.fiber_display.hits([4, 0, 3], [0, 0, -1])[0]["id"] == mirror
    controller.run("workspace.update", dict(mirror_display="SOURCE", hidden=[]))
    frames(controller)
    assert not controller.fiber_display.hits([4, 0, 3], [0, 0, -1])


def test_radius_replacement_switches_source_and_mirror_together(controller):
    _, key, mirror = setup(controller)
    old = rows(controller)[key]["handle"]
    radius(controller, key, 0.03)
    controller.session.wait(5)
    assert {r["handle"] for r in rows(controller).values()} == {old}
    frames(controller)
    displayed = rows(controller)
    assert displayed[key]["handle"] == displayed[mirror]["handle"] != old
    assert controller.fiber_display.hits([4, 0.02, 3], [0, 0, -1])[0]["id"] == mirror
    radius(controller, key, 0)
    frames(controller)
    assert not rows(controller) and not controller.fiber_display.accepted
    assert {r["id"] for r in controller.path_model.active_rows()} == {key, mirror}
