"""Contextual skin controls follow selection without changing the inspected document."""

from tests.test_quick_fiber import cube
from tests.test_quick_fiber_interaction import controller as controller


def test_skin_source_panel_tracks_selection_and_shared_commands(controller):
    target = cube(controller.session)
    before = controller.session.document
    controller.refresh()
    controller.selection_view.select(target)
    controller.refresh()
    state = controller.skin_panel.state["contributor"]
    assert state["owner"] == target and state["scp"] and state["editable"]
    assert controller.session.document is before
    controller.run("skin.collagen.fill", dict(owner=target, value=0.4))
    assert controller.skin_panel.state["contributor"]["settings"]["collagen_mode"] == "PAINTED"
    controller.run("undo", {})
    assert controller.skin_panel.state["contributor"]["settings"]["collagen_mode"] == "AUTO"
