"""The shared brush paints SCP collagen with staged colors and one undo."""

from tests.test_quick_fiber import cube
from tests.test_quick_fiber_interaction import controller as controller
from tests.test_tissue_inspection_view import publish
from tests.test_tissue_painting_view import preview


def brush(controller):
    target = cube(controller.session)
    controller.run("skin.collagen.fill", dict(owner=target, value=0))
    controller.refresh()
    controller.select(target)
    publish(controller)
    tool = controller.tissue_painting
    tool.beginCollagen()
    tool.setting("radius", 1000)
    tool.setting("through", True)
    return target, tool


def test_collagen_staged_preview_and_commit(controller):
    target, tool = brush(controller)
    before, cursor = controller.session.document, controller.session.history.cursor
    preview(controller, tool)
    assert tool.state["hiddenOwner"] == target
    assert tool.model.active_rows()[0]["kind"] == "HEAT"
    assert controller.session.document is before
    tool.release()
    controller.session.wait()
    publish(controller)
    assert controller.session.history.cursor == cursor + 1
    assert controller.session.document.skin != before.skin
    controller.run("undo", {})
    assert controller.session.document.skin == before.skin


def test_collagen_cancel_restores_surface(controller):
    _, tool = brush(controller)
    before = controller.session.document
    preview(controller, tool)
    controller.cancelViewportTools()
    publish(controller)
    assert not tool.state["hiddenOwner"] and not tool.state["active"]
    assert not tool.model.active_rows()
    assert controller.session.document is before
