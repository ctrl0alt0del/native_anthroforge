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
from ui_acceptance import click, find, resize_panel
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
    resize_panel(window)
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
    construction_search(controller, window)
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
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        QTest.qWait(200)
        scenarios(controller, window, report)
        assert not warnings, warnings
        (OUTPUT / "layout.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    finally:
        controller.close()
        delete(engine)
        application.processEvents()


def scenarios(controller, window, report):
    enum_contract(controller, window)
    tissue(controller, window, report)
    curve(controller, window, report)
    large_relationships(controller, window, report)


def large_relationships(controller, window, report):
    root = controller.session.document.entities[0].id
    for index in range(100):
        controller.session.command("scp.empty", name=f"Consumer {index:03}", parent=root)
    settle(controller)
    controller.select(root)
    click(window, "inspectTab")
    QTest.qWait(100)
    filter_relationships(window, report)
    outliner_hover(controller, window)


def construction_search(controller, window):
    before, selected = controller.session.document, controller.selection
    field = find(window, "constructionSearch")
    field.setProperty("text", "fiber")
    QTest.qWait(80)
    assert find(window, "constructionList").property("count") == 2
    field.setProperty("text", "no matching construction")
    QTest.qWait(80)
    assert find(window, "constructionList").property("count") == 0
    field.setProperty("text", "")
    assert controller.session.document is before and controller.selection == selected


def outliner_hover(controller, window):
    target = next(e.id for e in controller.session.document.entities if e.name == "Consumer 000")
    button = find(window, "delete_" + target)
    row = button.parentItem().parentItem()
    assert not button.isVisible()
    point = row.mapToScene(QPointF(25, row.height() / 2)).toPoint()
    QTest.mouseMove(window, point, 20)
    QTest.qWait(80)
    assert button.isVisible()
    point = button.mapToScene(QPointF(button.width() / 2, button.height() / 2)).toPoint()
    QTest.mouseMove(window, point, 20)
    QTest.qWait(80)
    assert button.isVisible()


def filter_relationships(window, report):
    search = reveal(window, "dependencyConsumers_poseSearch")
    assert search.isVisible()
    before = search.mapToScene(QPointF(0, 0))
    search.setProperty("text", "Consumer 099")
    QTest.qWait(100)
    assert find(window, "dependencyConsumers_poseList").property("count") == 1
    assert search.mapToScene(QPointF(0, 0)) == before
    snapshot(window, "relationship-search", report)


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
