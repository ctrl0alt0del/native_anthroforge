"""Offscreen project continuity interactions and inspector text audit at supported widths."""

import json
import os
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
OUTPUT = Path("build/usability-037/ui").resolve()
os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(OUTPUT / "state/preferences.json")

from PySide6.QtCore import QMetaObject, QPointF, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtQml import QQmlEngine, QQmlExpression
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from activity_acceptance import wait_for
from tissue_editor_acceptance import scene, settle
from ui_acceptance import click, find
from ui_polish_acceptance import descendants, open_menu

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime


def invoke(item, method):
    assert QMetaObject.invokeMethod(item, method, Qt.DirectConnection), method
    QTest.qWait(100)


def visible_text(item):
    if not item.isVisible() or item.metaObject().indexOfProperty("truncated") < 0:
        return False
    center, parent = QPointF(item.width() / 2, item.height() / 2), item.parentItem()
    while parent is not None:
        local = item.mapToItem(parent, center)
        if parent.clip() and not parent.boundingRect().contains(local):
            return False
        parent = parent.parentItem()
    return bool(item.property("text"))


def findings(window):
    rows = []
    for item in descendants(window.contentItem()):
        if not visible_text(item):
            continue
        clipped = item.property("truncated") or item.property("contentWidth") > item.width() + 1
        if clipped:
            rows.append(text_record(item))
    return rows


def text_record(item):
    return dict(
        text=item.property("text"),
        width=item.width(),
        height=item.height(),
        content=item.property("contentWidth"),
        parent=item.parentItem().objectName(),
    )


def capture(window, name, report):
    QTest.qWait(150)
    assert window.grabWindow().save(str(OUTPUT / (name + ".png")))
    report[name] = findings(window)


def inspect_widths(controller, window, name, report):
    for width, height in ((1440, 900), (1050, 680)):
        window.resize(width, height)
        settle(controller)
        capture(window, f"{name}-{width}", report)
        inspect_contents(window, f"{name}-{width}", report)


def inspect_contents(window, name, report):
    inspector = find(window, "inspector")
    panel = inspector.parentItem().parentItem()
    expression = QQmlExpression(
        QQmlEngine.contextForObject(panel), panel, "SplitView.preferredWidth=280"
    )
    expression.evaluate()
    assert not expression.hasError(), expression.error().toString()
    scroll = inspector.property("contentItem")
    QTest.qWait(80)
    bottom = max(0, scroll.property("contentHeight") - scroll.height())
    for index, position in enumerate(range(0, int(bottom) + 1, max(1, int(scroll.height() * 0.8)))):
        scroll.setProperty("contentY", position)
        capture(window, f"{name}-section-{index}", report)
    scroll.setProperty("contentY", 0)


def project_actions(controller, window, report):
    root = controller.run("primitive.create", dict(kind="BODY"))
    controller.select(root)
    settle(controller)
    target = OUTPUT / "Long project name with the same anatomy.anthroforge"
    controller.saveProject(str(target), "wait")
    settle(controller)
    assert controller.project_library.recent.entries[0] == str(target)
    inspect_widths(controller, window, "body", report)
    recent_menu(controller, window, report)
    recovery(controller, window, root, report)


def recent_menu(controller, window, report):
    library = controller.project_library
    library.remember(OUTPUT / "another folder" / Path(library.recent.entries[0]).name)
    menu = open_menu(window, "File")
    invoke(find(window, "recentProjectsMenu"), "open")
    capture(window, "recent-projects", report)
    invoke(find(window, "recentProjectsMenu"), "close")
    invoke(menu, "close")


def recovery(controller, window, root, report):
    controller.run("scp.rename", dict(entity=root, name="Recovered anatomy"))
    settle(controller)
    saver = controller.project_library.autosave
    saver.due = 0
    saver.poll(controller.session)
    settle(controller)
    assert saver.last and not saver.error
    controller.project_library.showRecovery()
    settle(controller)
    capture(window, "recovery-copies", report)
    assert find(window, "recoveryCopies").property("count") >= 1
    recovered_open(controller, window, saver.last["path"])


def recovered_open(controller, window, path):
    invoke(find(window, "recoveryDialog"), "close")
    before = controller.session.document
    controller.project_library.recovery_browser.openCopy(path)
    QTest.qWait(80)
    assert find(window, "discardDialog").property("visible")
    invoke(find(window, "discardDialog"), "close")
    controller.replaceDocument(path)
    wait_for(controller, lambda: not controller.session.waiting_save)
    assert controller.session.document == before
    assert controller.session.path is None and controller.session.saved_revision == -1
    assert path not in controller.project_library.recent.entries


def preferences(controller, window, report):
    invoke(find(window, "preferencesMenu"), "triggered")
    capture(window, "preferences", report)
    enabled = controller.session.preferences.value.autosave_enabled
    click(window, "autosaveEnabled")
    assert controller.session.preferences.value.autosave_enabled is not enabled
    click(window, "autosaveEnabled")
    invoke(find(window, "preferencesDialog"), "close")


def long_delete(controller, window, report):
    root = controller.session.document.entities[0].id
    controller.run("scp.rename", dict(entity=root, name="Long anatomical construction name " * 4))
    for index in range(24):
        controller.run("scp.empty", dict(parent=root, name=f"Attachment boundary number {index}"))
    settle(controller)
    controller.select(root)
    find(window, "viewport").forceActiveFocus()
    QTest.keyClick(window, Qt.Key.Key_Delete)
    QTest.qWait(100)
    assert find(window, "deleteDialog").property("visible")
    capture(window, "delete-many", report)
    search_delete(window)
    invoke(find(window, "deleteDialog"), "close")


def search_delete(window):
    field = find(window, "deleteAffectedSearch")
    before = field.mapToScene(QPointF(0, 0))
    field.setProperty("text", "number 23")
    QTest.qWait(80)
    assert find(window, "deleteAffectedObjects").property("count") == 1
    assert field.mapToScene(QPointF(0, 0)) == before


def construction(controller, window, report):
    controller.replaceDocument("")
    wait_for(controller, lambda: not controller.session.waiting_save)
    scene(controller)
    inspect_widths(controller, window, "surface", report)
    surface = controller.selection
    source = controller.session.document.object(surface).curves[0].curve
    controller.select(source)
    controller.authoring.setEditing(True)
    inspect_widths(controller, window, "fiber", report)
    controller.authoring.setEditing(False)
    controller.select(surface)
    controller.createConstruction("tissue.create", dict(source=surface))
    inspect_widths(controller, window, "tissue", report)


def exercise():
    controller, warnings, report = Controller(), [], {}
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        QTest.qWait(300)
        project_actions(controller, window, report)
        preferences(controller, window, report)
        long_delete(controller, window, report)
        construction(controller, window, report)
        (OUTPUT / "text-audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        assert not warnings, warnings
    finally:
        controller.close()
        engine.deleteLater()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        exercise()
        app.processEvents()
    print("Project continuity interactions passed; text audit captured offscreen.")


if __name__ == "__main__":
    main()
