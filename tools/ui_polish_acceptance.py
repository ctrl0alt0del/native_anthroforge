"""Real menu contrast, popup containment and compact-panel disclosure acceptance."""

import json
from pathlib import Path

import inspection_acceptance as inspection
import issues_acceptance as issues
from activity_acceptance import wait_for
from PySide6.QtCore import QObject, QPointF, Qt
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import click, find

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/ui-polish-019").resolve()


def descendants(item):
    pending, result = [item], []
    while pending:
        node = pending.pop()
        result.append(node)
        pending.extend(node.childItems())
    return result


def luminance(color):
    channels = (color.redF(), color.greenF(), color.blueF())
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return sum(c * weight for c, weight in zip(linear, (0.2126, 0.7152, 0.0722), strict=True))


def capture(window, name):
    QTest.qWait(100)
    assert window.grabWindow().save(str(OUTPUT / (name + ".png")))


def menu_hover(window, title):
    menu = open_menu(window, title)
    rows = descendants(menu.property("contentItem"))
    row = next(r for r in rows if r.objectName().startswith("menuItem") and r.isEnabled())
    point = row.mapToScene(QPointF(row.width() / 2, row.height() / 2)).toPoint()
    QTest.mouseMove(window, point)
    QTest.qWait(70)
    assert row.property("hovered") or row.property("highlighted")
    foreground = row.property("contentItem").childItems()[0].property("color")
    background = row.property("background").property("color")
    assert (luminance(foreground) + 0.05) / (luminance(background) + 0.05) >= 4.5
    capture(window, "menu-" + title.lower())
    QTest.keyClick(window, Qt.Key.Key_Escape)
    assert not menu.property("visible")


def combo_containment(window):
    click(window, "manageWorkspace")
    combo = click(window, "displayUnits")
    popup = combo.findChild(QObject, "comboPopup")
    view = popup.property("contentItem")
    rows = [r for r in descendants(view) if "ItemDelegate" in r.metaObject().className()]
    assert rows and all(r.width() <= view.width() for r in rows)
    assert all(r.property("leftPadding") == r.property("rightPadding") for r in rows)
    capture(window, "workspace-dropdown")
    QTest.keyClick(window, Qt.Key.Key_Escape)
    capture(window, "workspace")
    click(window, "closeWorkspace")


def disclosure_checks(controller, window):
    inspection.ruler(controller, window)
    assert not find(window, "measurementCoordinates").isVisible()
    capture(window, "measurements-compact")
    inspection.display_units(controller, window)
    inspection.bookmarks(controller, window)
    assert find(window, "measurementCoordinates").isVisible()
    capture(window, "measurements-details")
    click(window, "inspectionToolsToggle")
    menu_action(window, "Help", "Navigation and shortcuts")
    assert find(window, "shortcutHelp").property("visible")
    capture(window, "shortcuts")
    dialog_button(window, "shortcutHelp", "Close")


def issue_details(controller, window):
    controller.project_view.replaceDocument("")
    wait_for(controller, lambda: not controller.session.waiting_save)
    issues.create_cycle(controller)
    click(window, "issuesToggle")
    issues.select_first(controller, window)
    evidence = find(window, "issueEvidence")
    assert not evidence.isVisible()
    capture(window, "issues-compact")
    reveal_evidence(window)
    assert evidence.isVisible() and evidence.property("text")
    capture(window, "issues-evidence")


def menu_action(window, title, text):
    menu = open_menu(window, title)
    rows = descendants(menu.property("contentItem"))
    row = next(item for item in rows if item.property("text") == text)
    point = row.mapToScene(QPointF(row.width() / 2, row.height() / 2)).toPoint()
    QTest.mouseClick(window, Qt.LeftButton, pos=point)
    QTest.qWait(100)


def open_menu(window, title):
    click(window, "menuBar" + title)
    return find(window, "helpMenu" if title == "Help" else "menu" + title)


def reveal_evidence(window):
    panel = find(window, "issueDetails")
    toggle = find(window, "Details & evidenceToggle")
    position = toggle.mapToItem(panel, QPointF(0, 0)).y()
    panel.property("contentItem").setProperty("contentY", max(0, position - 20))
    QTest.qWait(80)
    click(window, "Details & evidenceToggle")


def dialog_button(window, name, text):
    dialog = find(window, name)
    buttons = descendants(dialog.property("footer"))
    button = next(item for item in buttons if item.property("text") == text)
    point = button.mapToScene(QPointF(button.width() / 2, button.height() / 2)).toPoint()
    QTest.mouseClick(window, Qt.MouseButton.LeftButton, pos=point)
    QTest.qWait(100)
    assert not dialog.property("visible")


def dialog_deletion(controller, window):
    root = controller.selection
    find(window, "viewport").forceActiveFocus()
    QTest.keyClick(window, Qt.Key.Key_Delete)
    assert not find(window, "deleteDialog").property("visible")
    assert not controller.session.document.entities
    controller.run("undo", {})
    controller.selection_view.select(root)
    assert controller.session.document.entity(root)


def layout_checks(window):
    for width, height in ((1440, 900), (1050, 680)):
        window.resize(width, height)
        QTest.qWait(120)
        assert find(window, "viewport").width() >= 300
        for title in ("File", "Edit", "View", "Help"):
            menu_hover(window, title)
        combo_containment(window)


def exercise(controller, window):
    inspection.fixture(controller)
    inspection.pickability(controller)
    layout_checks(window)
    window.resize(1440, 900)
    disclosure_checks(controller, window)
    dialog_deletion(controller, window)
    window.resize(1050, 680)
    issue_details(controller, window)


def run():
    controller, warnings = open_controller(None), []
    engine = create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        exercise(controller, engine.rootObjects()[0])
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    inspection.OUTPUT = OUTPUT
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        run()
    print(json.dumps(dict(ui_polish_acceptance=True, output=str(OUTPUT))))
