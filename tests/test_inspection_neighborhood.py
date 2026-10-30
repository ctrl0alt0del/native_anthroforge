"""Temporary inspection changes presentation alone and restores hidden objects and camera."""

from anthroforge.application import inspection_neighborhood
from anthroforge.desktop import inspection_visibility
from tests.test_fiber_creation import bind, scene
from tests.test_tissue_interaction import controller as controller


def test_neighborhood_includes_attached_fiber_without_changing_workspace(controller):
    session = controller.session
    target, curve = scene(session)
    fiber = bind(session, target, curve)
    controller.refresh()
    controller.selection_view.select(target)
    before, cursor = session.document, session.history.cursor
    controller.neighborhood.inspect()
    assert (
        fiber.id in controller.neighborhood.members and curve not in controller.neighborhood.members
    )
    controller.viewport_view.saveCamera([0, 0, 0, 0, 0, 0, 12], False)
    assert session.document is before and session.history.cursor == cursor
    controller.neighborhood.restore()
    assert not controller.neighborhood.members and session.document is before


def test_neighborhood_visibility_restores_original_flags(controller):
    target, _ = scene(controller.session)
    controller.refresh()
    controller.selection_view.select(target)
    row = hidden_record(target)
    controller.neighborhood.inspect()
    assert inspection_visibility.project(controller, row)["surface_visible"]
    controller.neighborhood.restore()
    assert inspection_visibility.project(controller, row) is row
    result = inspection_neighborhood.describe(controller.session, target)
    assert target in result["members"]


def hidden_record(target):
    return dict(
        id=target,
        visible=False,
        pickable=False,
        readonly=False,
        handle=123,
        surface_visible=False,
        surface_pickable=False,
    )
