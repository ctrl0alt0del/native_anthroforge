"""Existing UI refreshes publish shared eligibility without repeated status work."""

from anthroforge.application import replacement_status
from tests.test_mesh_replacement import source
from tests.test_tissue_interaction import controller as controller


def test_selected_replacement_button_tracks_edit_save_and_selection(controller):
    target = source(controller.session)
    controller.refresh()
    controller.select(target)
    panel = controller.mesh_replacement
    assert panel.eligibility["start"]["available"]
    controller.session.begin()
    controller.notify()
    assert not panel.eligibility["start"]["available"]
    controller.session.cancel()
    controller.notify()
    assert panel.eligibility["start"]["available"]
    controller.session.waiting_save = True
    controller.notify()
    assert not panel.eligibility["start"]["available"]


def test_idle_notifications_do_not_repeat_assessment(controller, monkeypatch):
    target = source(controller.session)
    controller.refresh()
    controller.select(target)
    calls, original = [], replacement_status.describe
    monkeypatch.setattr(
        replacement_status, "describe", lambda *a: (calls.append(a), original(*a))[1]
    )
    for _ in range(20):
        controller.mesh_replacement.synchronize()
    assert not calls
    controller.select("")
    assert not controller.mesh_replacement.eligibility["start"]["available"]
    assert calls
