"""Real offscreen workbench controls, retained operations and presentation invariants."""

import json
import os
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from tissue_editor_acceptance import scene, settle
from ui_acceptance import click, find
from usability_037_acceptance import findings

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path(os.environ.get("AF_WORKBENCH_OUTPUT", "build/ui-workbench/acceptance")).resolve()


def reveal(window, name):
    item, parent = find(window, name), find(window, name).parentItem()
    while parent is not None:
        if parent.metaObject().indexOfProperty("expanded") >= 0:
            parent.setProperty("expanded", True)
        parent = parent.parentItem()
    QTest.qWait(50)
    parent = item.parentItem()
    while parent is not None:
        if parent.metaObject().indexOfProperty("contentY") >= 0:
            point = item.mapToItem(parent, QPointF(0, 0))
            parent.setProperty("contentY", max(0, parent.property("contentY") + point.y() - 50))
        parent = parent.parentItem()
    QTest.qWait(50)
    return item


def activate(window, name):
    item = reveal(window, name)
    assert item.isVisible() and item.isEnabled(), name
    click(window, name)


def snapshot(window, name, report):
    QTest.qWait(150)
    assert window.grabWindow().save(str(OUTPUT / (name + ".png")))
    report[name] = findings(window)


def pages(controller, window, report):
    before = controller.session.document
    for name in ("inspectTab", "shortcutsTab", "shapeTab"):
        click(window, name)
        QTest.qWait(100)
        snapshot(window, name, report)
    assert controller.session.document is before
    assert find(window, "inspectorHeader").property("page") == "Shape"
    controller.workbench.setFocusEditor(True)
    QTest.qWait(100)
    snapshot(window, "focus-editor", report)
    controller.workbench.setFocusEditor(False)
    assert controller.session.document is before


def tissue(controller, window, report):
    scene(controller)
    activate(window, "createTissueToolbar")
    settle(controller)
    assert controller.selectedData["is_tissue"]
    for width, height in ((1440, 900), (1050, 680)):
        window.resize(width, height)
        snapshot(window, f"tissue-{width}", report)
    pages(controller, window, report)
    preview(controller, window)
    inspect(controller, window, report)
    activate(window, "tissueName")
    assert find(window, "tissueName").isVisible()
    snapshot(window, "tissue-source", report)


def preview(controller, window):
    before = controller.session.document
    activate(window, "tissuePreviewStart")
    settle(controller)
    click(window, "inspectTab")
    click(window, "shapeTab")
    assert find(window, "tissuePreviewCancel").isVisible()
    activate(window, "tissuePreviewCancel")
    assert controller.session.document is before


def inspect(controller, window, report):
    click(window, "inspectTab")
    assert find(window, "tissueCheckGeometry").isVisible()
    activate(window, "tissueCheckGeometry")
    settle(controller)
    snapshot(window, "geometry-findings", report)
    click(window, "issuesToggle")
    click(window, "shapeTab")


def enum_contract(controller, window):
    combo = find(window, "projectUpdateMode")
    combo.forceActiveFocus()
    QTest.keyClick(window, Qt.Key.Key_Down)
    QTest.qWait(80)
    assert combo.property("currentText") == "ON_RELEASE"
    assert combo.property("displayText") == "On release"
    assert controller.session.document.update_mode == "ON_RELEASE"
    QTest.keyClick(window, Qt.Key.Key_Up)
    QTest.qWait(80)


def curve(controller, window, report):
    sources = [o for o in controller.session.document.objects if type(o).__name__ == "Curve"]
    controller.select(sources[0].id)
    settle(controller)
    assert find(window, "inspectorHeader").property("page") == "Shape"
    activate(window, "editPrimitive")
    assert controller.authoring.state["editing"]
    before = controller.session.document
    click(window, "inspectTab")
    click(window, "shapeTab")
    assert controller.authoring.state["editing"]
    assert controller.session.document is before
    snapshot(window, "curve-editing", report)
    activate(window, "editPrimitive")


def exercise(application):
    controller, warnings, report = Controller(), [], {}
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        QTest.qWait(200)
        enum_contract(controller, window)
        tissue(controller, window, report)
        curve(controller, window, report)
        assert not warnings, warnings
        (OUTPUT / "layout.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    finally:
        controller.close()
        delete(engine)
        application.processEvents()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(OUTPUT / "state/preferences.json")
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        application = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        application.setFont(QFont("Segoe UI"))
        exercise(application)
    print("Workbench interactions and presentation invariants passed offscreen.")


if __name__ == "__main__":
    main()
