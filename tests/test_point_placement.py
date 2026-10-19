"""Gesture-level point placement preserves provisional data and coherent undo."""

import pytest
from PySide6.QtCore import QCoreApplication

from anthroforge.desktop.controller import Controller


@pytest.fixture
def controller():
    app = QCoreApplication.instance() or QCoreApplication([])
    value = Controller()
    value.timer.stop()
    yield value
    value.close()
    assert app


def click(tool, x, y=0, keep=False):
    tool.click([x, y, 3, 0, 0, -1, 500 + x * 50, 500 + y * 50, 1], [0, 0, -1], keep)


def test_plain_second_click_finishes_once_and_undo_restores_empty_document(controller):
    tool, session = controller.drawing_tools, controller.session
    tool.begin("POINTS")
    before = session.history.cursor
    click(tool, 0)
    assert tool.mode == "POINTS" and tool.state["count"] == 1 and not session.document.objects
    click(tool, 1)
    session.wait(5)
    assert not tool.mode and len(session.document.objects[0].points) == 2
    assert session.history.cursor == before + 1
    session.command("undo")
    assert not session.document.objects
    session.command("redo")
    session.wait(5)
    assert len(session.document.objects[0].points) == 2


def test_continuation_and_backspace_do_not_commit_provisional_points(controller):
    tool = controller.drawing_tools
    tool.begin("POINTS")
    for i in range(4):
        click(tool, i, keep=True)
    assert tool.mode == "POINTS" and not controller.session.document.objects
    tool.removeLast()
    assert tool.state["count"] == 3
    click(tool, 4)
    controller.session.wait(5)
    assert not tool.mode and len(controller.session.document.objects[0].points) == 4


def test_closed_early_finish_retains_draft_and_cancel_creates_nothing(controller):
    tool = controller.drawing_tools
    tool.setting("closed", True)
    tool.begin("POINTS")
    click(tool, 0)
    click(tool, 1)
    assert tool.mode == "POINTS" and tool.state["count"] == 2
    assert "three" in controller.message and not controller.session.document.objects
    click(tool, 1, 1)
    controller.session.wait(5)
    assert controller.session.document.objects[0].closed and not tool.mode
    tool.begin("POINTS")
    click(tool, 5)
    tool.cancel()
    assert len(controller.session.document.objects) == 1
