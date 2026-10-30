"""Selection routing shares source validation and accepted creation lifecycle."""

import pytest
from PySide6.QtCore import QCoreApplication

from anthroforge.core.surfaces import Surface
from anthroforge.desktop.controller import Controller
from tests.test_surface_workflow import curve


@pytest.fixture
def controller():
    app = QCoreApplication.instance() or QCoreApplication([])
    value = Controller()
    value.timer.stop()
    yield value
    value.close()
    assert app


def select(controller, keys):
    controller.refresh()
    for index, key in enumerate(keys):
        controller.selection_view.select(key, index > 0)


@pytest.mark.parametrize("count", [2, 3])
def test_surface_action_lofts_in_selection_order_and_selects_accepted_result(controller, count):
    session = controller.session
    keys = [curve(session, y=index) for index in range(count)]
    select(controller, keys)
    before = session.history.cursor
    assert controller.construction_view.surfaceAction["enabled"]
    controller.construction_view.createSurface("AUTO")
    session.wait()
    controller.refresh()
    result = session.document.object(controller.selection)
    assert isinstance(result, Surface) and result.kind == "LOFT" and result.result.status == "ready"
    assert [use.curve for use in result.curves] == keys and not session.document.entities
    assert session.history.cursor == before + 1


def test_single_closed_curve_creates_patch_and_exits_edit_mode(controller):
    session = controller.session
    key = curve(session, closed=True)
    select(controller, [key])
    controller.authoring.setEditing(True)
    assert controller.construction_view.surfaceAction["enabled"]
    controller.construction_view.createSurface("AUTO")
    session.wait()
    controller.refresh()
    item = session.document.object(controller.selection)
    assert isinstance(item, Surface) and item.kind == "PATCH" and item.result.status == "ready"
    assert item.curves[0].curve == key and not controller.authoring.editing


def test_invalid_selection_uses_same_validation_and_never_starts_job(controller):
    assert not controller.construction_view.surfaceAction["enabled"]
    session = controller.session
    keys = [curve(session), curve(session, closed=True)]
    for selection in ([keys[0]], keys):
        select(controller, selection)
        assert not controller.construction_view.surfaceAction["enabled"]
        before, cursor = session.document, session.history.cursor
        controller.construction_view.createSurface("AUTO")
        assert session.document == before and session.history.cursor == cursor
        assert controller.message and not any(job.active for job in session.scheduler.jobs)
