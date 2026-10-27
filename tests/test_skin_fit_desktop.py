"""Desktop fitting uses shared eligibility and saved-result operations."""

from tests.test_quick_fiber_interaction import controller as controller
from tests.test_skin_fit_jobs import fit, setup


def test_shortcut_readiness_saved_fit_selection_and_preview(controller):
    session = controller.session
    identity = setup(session)
    editor = controller.shortcut_panel.editor
    editor.select(identity)
    assert editor.fitEligibility["available"] and editor.fitEligibility["dimension"] == "LENGTH"
    item = fit(session, identity)
    controller.refresh()
    panel = controller.skin_panel.fits
    panel.select(item.id)
    assert panel.state["id"] == item.id and panel.results.rowCount() == 1
    panel.preview(0.1)
    session.wait()
    controller.refresh()
    assert panel.previewState["visible"]
