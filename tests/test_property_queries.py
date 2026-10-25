"""Metadata notifications follow authored policies, not unrelated accepted results."""

from dataclasses import replace

import pytest
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine
from shiboken6 import delete

from tests.test_driving_formulas import curve, driver, reference
from tests.test_tissue_interaction import controller as controller

METADATA_QML = b"""import QtQml
    QtObject { readonly property bool writable: panel.propertyState(reference,
        panel.propertyQueries.versions[reference.target] || 0).writable }"""


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


@pytest.fixture
def qml_metadata(controller):
    target = curve(controller.session)
    engine = QQmlEngine()
    engine.rootContext().setContextProperty("panel", controller.shortcut_panel)
    engine.rootContext().setContextProperty("reference", reference(target))
    component = QQmlComponent(engine)
    component.setData(METADATA_QML, QUrl())
    root = component.create()
    assert root is not None, component.errors()
    yield root, target
    delete(root)
    delete(engine)


def test_qml_metadata_binding_updates_without_document_revision(controller, qml_metadata):
    root, target = qml_metadata
    assert root.property("writable")
    key, formula = driver(controller.session, target, "8")
    controller.session.wait(5)
    controller.shortcut_panel.property_queries.synchronize()
    assert not root.property("writable")
    controller.session.command("driver.formula.remove", driver=key, formula=formula)
    controller.shortcut_panel.property_queries.synchronize()
    assert root.property("writable")


def test_hook_membership_change_unlocks_cached_resolution(controller):
    from tests.test_parametric_deformation import body_and_hook

    session, panel = controller.session, controller.shortcut_panel
    target, _, _, binding = body_and_hook(session, restricted=True)
    ref = reference(target)
    assert not panel.propertyState(ref, 0)["writable"]
    session.command("deformer.remove", binding=binding)
    assert panel.propertyState(ref, 0)["writable"]


def test_lazy_metadata_read_defers_qml_notifications(controller):
    from PySide6.QtCore import QCoreApplication

    panel = controller.shortcut_panel
    ref = reference(curve(controller.session))
    panel.propertyState(ref, 0)
    panel.property_queries.publish()
    original = panel.property_queries.epochs.value(ref["target"])
    controller.session.command("shortcut.expose", reference=ref, exposed=True)
    assert panel.propertyState(ref, 0)["exposed"]
    assert panel.property_queries.epochs.value(ref["target"]) == original
    assert panel.property_queries.pending
    QCoreApplication.processEvents()
    assert panel.property_queries.epochs.value(ref["target"]) == panel.property_queries.serial
    assert not panel.property_queries.pending
