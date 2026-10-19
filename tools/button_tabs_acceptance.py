"""Check real tab navigation and shared button alignment in the offscreen editor."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
if os.name == "nt":
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ["SystemRoot"], "Fonts"))

import json
from pathlib import Path

from feedback_fixes_acceptance import settle, setup
from PySide6.QtCore import QPointF, Qt
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import click, find
from ui_polish_acceptance import descendants, luminance

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/tab-and-icon-alignment") / os.environ.get("QT_SCALE_FACTOR", "1")


def parts(button):
    items = descendants(button.property("contentItem"))
    return [
        item
        for item in items
        if item.isVisible() and item.metaObject().className() in ("QQuickImage", "QQuickText")
    ]


def bounds(button):
    boxes = []
    for item in parts(button):
        point = item.mapToItem(button, QPointF())
        boxes.append((point.x(), point.y(), point.x() + item.width(), point.y() + item.height()))
    assert boxes, button.objectName()
    return [
        min(b[0] for b in boxes),
        min(b[1] for b in boxes),
        max(b[2] for b in boxes),
        max(b[3] for b in boxes),
    ]


def check_button(button):
    x, y, right, bottom = bounds(button)
    name = button.objectName() or button.property("text") or button.property("glyph")
    assert x >= -0.5 and y >= -0.5, (name, bounds(button))
    assert right <= button.width() + 0.5 and bottom <= button.height() + 0.5, name
    assert abs((y + bottom - button.height()) / 2) <= 0.5, name
    if button.property("alignLeft"):
        assert abs(x - button.property("leftPadding")) <= 0.5, name
    else:
        assert abs((x + right - button.width()) / 2) <= 0.5, name
    return dict(name=name, size=[button.width(), button.height()], content=[x, y, right, bottom])


def check_buttons(window):
    buttons = [b for b in descendants(window.contentItem()) if b.property("glyph") is not None]
    return [check_button(b) for b in buttons if b.isVisible() and b.opacity() > 0]


def capture(window, name):
    QTest.qWait(80)
    assert window.grabWindow().save(str(OUTPUT / (name + ".png")))


def assert_tab(window, index):
    assert find(window, "objectTabs").property("currentIndex") == index
    for number, (tab, pane) in enumerate(
        (
            ("anatomyTab", "hierarchy"),
            ("constructionTab", "constructionList"),
        )
    ):
        assert find(window, tab).property("checked") == (number == index)
        assert find(window, pane).isVisible() == (number == index)


def tab_navigation(window, controller, root):
    tab = click(window, "anatomyTab")
    tab.forceActiveFocus(Qt.TabFocusReason)
    QTest.keyClick(window, Qt.Key_Right)
    assert_tab(window, 1)
    QTest.keyClick(window, Qt.Key_Left)
    assert_tab(window, 0)
    search = click(window, "outlinerSearch")
    for letter in "cube":
        QTest.keyClick(window, letter)
    click(window, "constructionTab")
    click(window, "anatomyTab")
    assert search.property("text") == "cube"
    search.setProperty("text", "")
    selection_navigation(window, controller, root)


def selection_navigation(window, controller, root):
    click(window, "addCurveAtCursor")
    settle(controller)
    assert_tab(window, 1)
    curve = controller.selection
    controller.authoring.setEditing(False)
    controller.select(root)
    QTest.qWait(80)
    assert_tab(window, 0)
    controller.select(curve)
    QTest.qWait(80)
    assert_tab(window, 1)
    controller.select(root)
    QTest.qWait(80)


def control_states(window, root):
    button = find(window, "delete_" + root)
    point = button.mapToScene(QPointF(button.width() / 2, button.height() / 2)).toPoint()
    QTest.mouseMove(window, point)
    QTest.qWait(70)
    assert button.property("hovered")
    check_button(button)
    button.forceActiveFocus(Qt.TabFocusReason)
    assert button.property("activeFocus")
    capture(window, "delete-hover-focus")
    button.setProperty("enabled", False)
    check_button(button)
    capture(window, "delete-disabled")
    button.setProperty("enabled", True)
    help_state(window)


def long_label(window):
    button = find(window, "addObjectImage")
    original = button.property("text")
    button.setProperty("text", "A long label that must elide without consuming its padding " * 3)
    QTest.qWait(80)
    assert button.property("leftPadding") == button.property("rightPadding") == 8
    check_button(button)
    capture(window, "long-label")
    button.setProperty("text", original)


def help_state(window):
    buttons = descendants(window.contentItem())
    help_button = next(b for b in buttons if b.isVisible() and b.property("text") == "?")
    point = help_button.mapToScene(QPointF(12, 12)).toPoint()
    QTest.mouseMove(window, point)
    QTest.qWait(70)
    assert help_button.property("hovered")
    check_button(help_button)
    foreground = parts(help_button)[0].property("color")
    background = help_button.property("background").property("color")
    assert (luminance(foreground) + 0.05) / (luminance(background) + 0.05) >= 4.5
    capture(window, "help-hover")


def layouts(window):
    rows = {}
    for width, height in ((1440, 900), (1050, 680)):
        window.resize(width, height)
        for tab in ("anatomyTab", "constructionTab"):
            click(window, tab)
            rows[f"{tab}-{width}"] = check_buttons(window)
            capture(window, f"{tab}-{width}")
    (OUTPUT / "alignment.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        window, root = engine.rootObjects()[0], setup(controller)
        window.resize(1440, 900)
        exercise(window, controller, root)
        assert not warnings, warnings
        print(json.dumps(dict(passed=True, scale=window.devicePixelRatio(), output=str(OUTPUT))))
    finally:
        controller.close()
        delete(engine)


def exercise(window, controller, root):
    tab_navigation(window, controller, root)
    control_states(window, root)
    long_label(window)
    layouts(window)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run()
        finally:
            delete(app)
