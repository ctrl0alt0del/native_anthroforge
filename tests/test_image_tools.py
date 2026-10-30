"""Image dialog intent survives selection changes but not a document/workspace switch."""

from tests.test_fiber_interaction import controller as controller
from tests.test_fiber_interaction import settle
from tests.test_reference_images import source


def test_parent_and_owner_are_captured_before_file_picker(controller, tmp_path):
    parent = controller.run("scp.empty", dict(name="Parent"))
    controller.selection_view.select(parent)
    tool = controller.image_tools
    assert tool.prepareImport(parent, "X")
    other = controller.run("curve.create", {})
    controller.selection_view.select(other)
    tool.acceptImport(source(tmp_path))
    settle(controller)
    item = controller.session.document.object(controller.selection)
    assert item.parent == parent and item.owners == (parent,)
    assert not tool.import_request


def test_world_import_never_implicitly_parents_to_selection(controller, tmp_path):
    parent = controller.run("scp.empty", dict(name="Parent"))
    controller.selection_view.select(parent)
    assert controller.image_tools.prepareImport("", "Z")
    controller.image_tools.acceptImport(source(tmp_path))
    settle(controller)
    item = controller.session.document.object(controller.selection)
    assert not item.parent and item.owners == (parent,)


def test_cancel_and_document_change_discard_import_intent(controller, tmp_path):
    tool = controller.image_tools
    assert tool.prepareImport("", "")
    tool.cancelImport()
    tool.acceptImport(source(tmp_path))
    assert not controller.session.scheduler.jobs
    assert tool.prepareImport("", "Y")
    from anthroforge.desktop.controller_actions import new_document

    new_document(controller)
    tool.acceptImport(source(tmp_path))
    assert not controller.session.document.objects
    assert "document or workspace changed" in controller.message
