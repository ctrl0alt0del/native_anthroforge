"""Metadata notifications follow authored policies, not unrelated accepted results."""

from dataclasses import replace

from tests.test_driving_formulas import curve, driver, reference
from tests.test_tissue_interaction import controller as controller


def test_result_publication_keeps_property_metadata_subscription(controller):
    session, panel = controller.session, controller.shortcut_panel
    target = curve(session)
    ref = reference(target)
    original = panel.propertyState(ref, 0)
    item = session.document.object(target)
    updated = replace(item, result=replace(item.result, revision=item.result.revision + 1))
    session.replace_document(objects=(updated,))
    panel.property_queries.synchronize()
    assert panel.propertyState(ref, 1) is original
    assert panel.property_queries.serial == 0


def test_formula_and_exposure_edits_refresh_metadata_with_undo(controller):
    session, panel = controller.session, controller.shortcut_panel
    ref = reference(curve(session))
    assert panel.propertyState(ref, 0)["writable"]
    session.command("shortcut.expose", reference=ref, exposed=True)
    assert panel.propertyState(ref, 0)["exposed"]
    key, formula = driver(session, ref["target"], "8")
    session.wait(5)
    assert panel.propertyState(ref, 0)["driver"] == key
    session.command("driver.formula.remove", driver=key, formula=formula)
    assert panel.propertyState(ref, 0)["writable"]
    session.command("undo")
    session.wait(5)
    assert not panel.propertyState(ref, 0)["writable"]
