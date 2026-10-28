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


def test_authoring_only_result_explains_unavailable_desktop_refit(controller):
    session = controller.session
    identity = setup(session)
    session.command(
        "skin.fit.authoring",
        shortcut=identity,
        settings=dict(minimum=0, maximum=0.2, bones=1, samples=5, strategy="SINGLE_ACTIVE"),
    )
    session.wait()
    panel = controller.skin_panel.fits
    panel.select(session.document.skin.fits[-1].id)
    assert not panel.refitEligibility["available"]
    assert "authoring" in panel.refitEligibility["reason"]
