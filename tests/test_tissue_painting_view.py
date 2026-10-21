"""Desktop strokes preserve staged geometry, selection, cancellation and coherent undo."""

from anthroforge.desktop.tissue_inspection_scene import primary
from tests.test_tissue_inspection_view import publish
from tests.test_tissue_interaction import controller as controller
from tests.test_tissue_painting import setup
from tests.test_tissue_painting_native import VIEW


def brush(controller):
    target = setup(controller.session)
    controller.refresh()
    controller.select(target)
    tool = controller.tissue_painting
    tool.begin("paint")
    publish(controller)
    tool.setting("radius", 1000)
    tool.setting("through", True)
    return target, tool


def preview(controller, tool):
    tool.pointer([0, 0], list(VIEW), True)
    tool.timer.stop()
    tool.submit()
    controller.session.wait()
    publish(controller)


def test_paint_colors_and_one_undo_on_release(controller):
    target, tool = brush(controller)
    before, cursor = controller.session.document, controller.session.history.cursor
    preview(controller, tool)
    assert primary(controller.tissue_inspection)["kind"] == "HEAT"
    assert controller.session.document is before and tool.dragging
    tool.release()
    controller.session.wait()
    publish(controller)
    controller.session.wait()
    assert controller.session.history.cursor == cursor + 1
    assert any(controller.session.document.object(target).fields[0].values)
    controller.session.command("undo")
    controller.session.wait()
    assert controller.session.document.object(target).fields == before.object(target).fields


def test_escape_discards_paint_and_keeps_original_weights(controller):
    target, tool = brush(controller)
    before = controller.session.document
    preview(controller, tool)
    controller.cancelViewportTools()
    publish(controller)
    assert controller.session.document is before and not tool.name
    assert primary(controller.tissue_inspection)["kind"] == "MESH"
    assert not any(before.object(target).fields[0].values)


def test_pending_paint_replacement_keeps_previous_colors(controller):
    _, tool = brush(controller)
    preview(controller, tool)
    previous = primary(controller.tissue_inspection)["handle"]
    tool.pointer([20, 0], list(VIEW), False)
    tool.timer.stop()
    tool.submit()
    controller.notify()
    assert primary(controller.tissue_inspection)["handle"] == previous
    tool.cancel()
