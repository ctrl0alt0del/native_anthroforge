"""Historical rendering obeys current presentation and retains interaction boundaries."""

from tests.test_construction_contracts import create
from tests.test_shortcut_comparison import baseline
from tests.test_tissue_interaction import controller as controller


def test_history_obeys_geometry_and_curve_visibility(controller):
    session, view = controller.session, controller.shortcut_comparison
    create(session, kind="BODY")
    baseline(session)
    view.synchronize()
    view.setMode("Before")
    session.command("workspace.update", hidden_categories=["geometry"])
    view.synchronize()
    assert view.model.wanted and all(r["kind"] == "PATH" for r in view.model.wanted.values())
    session.command("workspace.update", hidden_categories=["curves"])
    view.synchronize()
    assert view.model.wanted and all(r["kind"] == "MESH" for r in view.model.wanted.values())


def test_before_waits_for_staging_and_direct_edits_switch_after(controller):
    session, view = controller.session, controller.shortcut_comparison
    _, key = baseline(session)
    view.synchronize()
    view.setMode("Before")
    assert not view.before
    present(view.model)
    assert view.before
    session.command("driver.value", driver=key, value=24)
    view.synchronize()
    assert view.mode == "After"
    assert session.history.before is None


def present(model):
    while model.pending:
        model.drain()
    model.presented()
    model.presented()
