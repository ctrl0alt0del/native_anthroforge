"""Desktop strokes preserve staged geometry, selection, cancellation and coherent undo."""

from anthroforge.desktop.tissue_inspection_scene import primary
from tests.test_tissue_inspection_view import publish
from tests.test_tissue_interaction import controller as controller
from tests.test_tissue_painting import setup
from tests.test_tissue_painting_native import VIEW


def brush(controller):
    target = setup(controller.session)
    controller.refresh()
    controller.selection_view.select(target)
    tool = controller.tissue_painting
    tool.begin("paint")
    publish(controller)
    tool.setting("radius", 1000)
    tool.setting("through", True)
    return target, tool


def preview(controller, tool):
    tool.pointer([0, 0], list(VIEW), True)
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
    controller.viewport_view.cancelViewportTools()
    publish(controller)
    assert controller.session.document is before and not tool.name
    assert primary(controller.tissue_inspection)["kind"] == "MESH"
    assert not any(before.object(target).fields[0].values)


def test_pending_paint_replacement_keeps_previous_colors(controller):
    _, tool = brush(controller)
    preview(controller, tool)
    previous = primary(controller.tissue_inspection)["handle"]
    tool.pointer([20, 0], list(VIEW), False)
    controller.notify()
    assert primary(controller.tissue_inspection)["handle"] == previous
    tool.cancel()


def test_camera_metadata_save_does_not_cancel_active_stroke(controller):
    target, tool = brush(controller)
    preview(controller, tool)
    controller.viewport_view.saveCamera([0, 0, 0, -35, -25, 0, 2.3], True)
    tool.synchronize()
    assert tool.dragging and tool.preview
    tool.release()
    controller.session.wait()
    publish(controller)
    controller.session.wait()
    assert any(controller.session.document.object(target).fields[0].values)


def test_finished_stroke_allows_hover_and_ignores_duplicate_pointer(controller):
    _, tool = brush(controller)
    preview(controller, tool)
    tool.pointer([0, 0], list(VIEW), False)
    assert tool.stroke_state()["sequence"] == 1
    tool.release()
    controller.session.wait()
    publish(controller)
    assert not tool.options
    tool.pointer([0, 0], list(VIEW), False)
    controller.session.wait()
    publish(controller)
    assert tool.preview and not tool.dragging
