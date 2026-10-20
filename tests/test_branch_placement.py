"""Real placement uses displayed controls and native projected nearest-point queries."""

import numpy as np

from anthroforge.native.components import PickIndex
from tests.test_branch_creation import curve
from tests.test_point_placement import click
from tests.test_point_placement import controller as controller


def displayed(controller):
    source = curve(controller.session)
    controller.session.wait()
    controller.refresh()
    for _ in range(4):
        controller.path_model.drain()
        controller.path_model.presented()
    return source


def test_preview_seed_finish_and_single_undo(controller):
    source = displayed(controller)
    tool, session = controller.drawing_tools, controller.session
    tool.begin("BRANCH")
    tool.pointer([0.1, 1.1, 3, 0, 0, -1, 500, 500, 1], [0, 0, -1], False)
    np.testing.assert_allclose(tool.hover, [0, 1, 0])
    assert not session.document.junctions
    click(tool, 0.1, 1.1)
    assert tool.state["count"] == 1 and not session.document.junctions
    click(tool, 1, 1.5)
    session.wait()
    assert not tool.mode and session.document.objects[-1].points[0].junction
    session.command("undo")
    assert len(session.document.objects) == 1 and session.document.object(source)


def test_backspace_retargets_and_cancel_does_not_mutate(controller):
    displayed(controller)
    tool, before = controller.drawing_tools, controller.session.document
    tool.begin("BRANCH")
    click(tool, 0, 1)
    tool.removeLast()
    assert not tool.branch.source
    click(tool, 0, 2)
    np.testing.assert_allclose(tool.stroke.read()[0, :3], [0, 2, 0])
    click(tool, 1, 2, keep=True)
    assert tool.mode == "BRANCH" and tool.stroke.count == 2
    tool.cancel()
    assert controller.session.document == before and tool.stroke is None


def test_hidden_unpickable_and_behind_camera_points_are_excluded(controller):
    source = displayed(controller)
    controller.run("workspace.update", dict(hidden=[source]))
    controller.path_model.presented()
    controller.drawing_tools.begin("BRANCH")
    click(controller.drawing_tools, 0, 1)
    assert not controller.drawing_tools.branch.source
    index = PickIndex(controller.session.engine, [[0, 0, -1], [0.2, 0, 1]])
    assert index.closest([0, 0, 0], [0, 0, 1], [0, 0, 1], True) == 1


def test_native_nearest_prefers_projected_distance_not_nearest_depth(controller):
    index = PickIndex(controller.session.engine, [[0.1, 0, 1], [0.2, 0, 10], [0, 0, -2]])
    assert index.closest([0, 0, 0], [0, 0, 1], [0, 0, 1], True) == 1
    assert index.closest([0, 0, 0], [0, 0, 1], [0, 0, 1], False) == 0
