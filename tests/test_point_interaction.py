"""Desktop construction rows, creation selection and native point picking."""

import pytest
from PySide6.QtCore import QCoreApplication

from anthroforge.core.points import Anchor
from anthroforge.desktop.controller import Controller
from tests.test_anchor_operations import CUBE


@pytest.fixture
def controller():
    app = QCoreApplication.instance() or QCoreApplication([])
    controller = Controller()
    controller.timer.stop()
    yield controller
    controller.close()
    assert app


def test_point_creation_selects_and_native_hover_matches_click(controller):
    controller.run("workspace.update", dict(cursor=[1, 2, 3]))
    controller.construction_view.createPoint()
    key = controller.selection
    assert controller.selection_view.selectedData["kind"] == "POINT"
    assert controller.selection_view.selectedData["world_position"] == [1, 2, 3]
    hovered = controller.selection_view.pick([1, 2, 5], [0, 0, -1], 0, False, 0.03)
    clicked = controller.selection_view.pick([1, 2, 5], [0, 0, -1], 0, True, 0.03)
    assert hovered["id"] == clicked["id"] == key
    assert controller.viewport_view.selectionCenter() == [1, 2, 3]


def test_independent_anchor_becomes_selection_and_exposes_explicit_surface_role(controller):
    session = controller.session
    bone = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait()
    controller.construction_view.createPoint()
    source = controller.selection
    controller.construction_view.createConstruction(
        "anchor.create", dict(source=source, parent=bone)
    )
    session.wait()
    controller.refresh()
    assert isinstance(session.document.object(controller.selection), Anchor)
    assert controller.selection_view.selectedData["binding"]["reference"] == dict(
        target=bone, role="SCP_GEOMETRY", instance=""
    )
    assert not controller.selection_view.selectedData["transformable"]
    assert controller.construction_view.surfaceRoles()[0]["role"] == "SCP_GEOMETRY"


def test_hidden_points_are_not_pickable_and_pick_cache_tracks_changes(controller):
    controller.construction_view.createPoint()
    key = controller.selection
    controller.run("construction.point.update", dict(target=key, position=[2, 0, 0]))
    assert not controller.selection_view.pick([0, 0, 3], [0, 0, -1], 0, False, 0.03)
    assert controller.selection_view.pick([2, 0, 3], [0, 0, -1], 0, False, 0.03)["id"] == key
    controller.run("workspace.update", dict(hidden=[key]))
    assert not controller.selection_view.pick([2, 0, 3], [0, 0, -1], 0, False, 0.03)
