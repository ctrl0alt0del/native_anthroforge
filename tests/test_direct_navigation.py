"""Source/member navigation changes presentation, not authored geometry or history."""

import pytest

from tests.test_fiber_interaction import controller as controller
from tests.test_fiber_interaction import settle


def target(controller, stage):
    controller.authoring.create("BODY", "CAPSULE")
    settle(controller)
    owner = controller.selection
    if stage == "LATTICE":
        owner = controller.run("control.create", dict(kind="LATTICE", entity=owner))
        controller.select(owner)
    controller.authoring.setEditing(True)
    controller.authoring.setCategory(stage)
    return owner


@pytest.mark.parametrize("stage", ["CURVE", "BASE", "LATTICE"])
def test_select_hook_members_enters_correct_editor_without_authored_edits(controller, stage):
    owner = target(controller, stage)
    editor = controller.authoring
    editor.selectComponent(editor.componentRows[0]["key"], False)
    editor.addDeformer("HOOK")
    settle(controller)
    binding = controller.session.document.object(owner).deformers[0]
    before, cursor = controller.session.document, controller.session.history.cursor
    editor.setEditing(False)
    editor.members(binding.id, False)
    assert controller.selection == owner and editor.editing
    assert editor.category == stage and len(editor.selection) == 1
    assert controller.session.document == before and controller.session.history.cursor == cursor
