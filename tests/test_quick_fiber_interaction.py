"""The same desktop placement gesture keeps clicks provisional until one shared operation."""

import pytest
from PySide6.QtCore import QCoreApplication

from anthroforge.core.fibers import Fiber
from anthroforge.desktop.controller import Controller
from tests.test_quick_fiber import cube


@pytest.fixture
def controller():
    app = QCoreApplication.instance() or QCoreApplication([])
    value = Controller()
    value.timer.stop()
    yield value
    value.close()
    assert app


def click(tool, x, continued=False):
    tool.click([x, 0, 3, 0, 0, -1, 100 + x * 100, 100, 1], [0, 0, -1], continued)


def settle(controller):
    controller.session.wait(5)
    controller.refresh()
    for _ in range(8):
        controller.render_model.drain()
        controller.frame_presented()


def test_surface_clicks_continue_finish_and_select_bound_routed_fiber(controller):
    target = cube(controller.session)
    settle(controller)
    tool, count = controller.drawing_tools, len(controller.session.history.entries)
    tool.begin("FIBER")
    click(tool, -0.4)
    click(tool, 0, True)
    assert tool.point_count() == 2 and not controller.session.document.objects
    click(tool, 0.4)
    settle(controller)
    fiber = controller.session.document.object(controller.selection)
    assert isinstance(fiber, Fiber) and fiber.engine == "ROUTED"
    assert len(fiber.bindings) == 3 and {b.target for b in fiber.bindings} == {target}
    assert len(controller.session.history.entries) == count + 1 and not tool.mode


def test_misses_pop_and_cancel_never_create_an_authored_draft(controller):
    cube(controller.session)
    settle(controller)
    tool, cursor = controller.drawing_tools, controller.session.history.cursor
    tool.begin("FIBER")
    click(tool, 3)
    assert tool.point_count() == 0 and not tool.hover
    click(tool, 0)
    assert len(tool.hover) == 3
    tool.removeLast()
    assert tool.point_count() == 0
    click(tool, 0)
    tool.cancel()
    assert not tool.fiber.points and not tool.mode
    assert not controller.session.document.objects and controller.session.history.cursor == cursor
