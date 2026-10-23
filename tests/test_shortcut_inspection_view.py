"""Inspection lifetime follows the editor, queries and displayed revisions."""

from dataclasses import replace

from anthroforge.application import shortcut_effects, tissue_inspection
from anthroforge.desktop.shortcut_inspection_view import badge
from tests.test_driving_formulas import curve, driver, reference
from tests.test_shortcut_copy import hierarchy
from tests.test_tissue_interaction import controller as controller


def select(controller, target):
    key = controller.session.command(
        "shortcut.expose", reference=reference(target, ("transform", "scale"), 0)
    )
    panel = controller.shortcut_panel
    panel.configure(True, True, "")
    panel.editor.select(key)
    panel.editor.inspection.activate(True)
    return key, panel.editor.inspection


def test_show_effects_queries_only_on_request_and_hides_on_editor_exit(controller):
    _, child = hierarchy(controller.session)
    _, view = select(controller, child)
    assert tissue_inspection.status(controller.session, "shortcut")["state"] == "idle"
    before = controller.session.document
    view.showEffects(True)
    controller.session.wait(5)
    controller.shortcut_panel.synchronize()
    assert view.value["anchors"]["state"] == "ready"
    assert view.value["anchors"]["report"]["rows"][0]["authored_anchors"]["available"]
    assert controller.session.document is before
    controller.shortcut_panel.configure(False, True, "")
    assert not view.snapshot() and anchor_state(controller) == "idle"


def anchor_state(controller):
    return tissue_inspection.status(controller.session, "shortcut")["state"]


def test_cancel_badge_does_not_reuse_completed_result_label(controller):
    target = curve(controller.session)
    key, _ = driver(controller.session, target, "round(value)", value=8)
    controller.session.wait(5)
    controller.session.begin()
    controller.session.command("driver.value", driver=key, value=12)
    controller.session.wait(5)
    controller.session.cancel()
    assert badge(controller.shortcut_panel, key) == "Cancelled"


def test_pending_input_evidence_does_not_imply_work_is_still_running(controller):
    root = curve(controller.session)
    controller.session.wait(5)
    item = controller.session.document.object(root)
    result = replace(item.result, pending=(root,))
    assert shortcut_effects.current_pending(controller.session.document, result) == []
    controller.session.command("update_mode", entity=root, mode="MANUAL")
    controller.session.command("property.set", reference=reference(root), value=37)
    assert shortcut_effects.current_pending(controller.session.document, result) == [root]


def test_formula_reports_expression_that_produced_the_accepted_evidence(controller):
    session = controller.session
    target = curve(session)
    key, formula = driver(session, target, "round(value)", value=8)
    session.wait(5)
    report = session.command("shortcut.formulas", shortcut=key)["rows"][0]
    assert report["evaluated_expression"] == "round(value)"
    session.command(
        "driver.formula.update", driver=key, formula=formula, changes=dict(expression="0/0")
    )
    session.wait(5)
    report = session.command("shortcut.formulas", shortcut=key)["rows"][0]
    assert report["result"]["status"] == "failed" and report["evaluated_expression"] == "0/0"
