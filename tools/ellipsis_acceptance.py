"""Narrow production inspectors and complete popup choices, using offscreen windows only."""

import os
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from numeric_input_acceptance import reveal
from PySide6.QtCore import QMetaObject, QObject, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtQml import QQmlEngine, QQmlExpression
from PySide6.QtTest import QTest
from tissue_editor_acceptance import (
    QQuickStyle,
    delete,
    native_runtime,
    profiler_application,
    run,
    scene,
    settle,
)
from ui_acceptance import click, find
from ui_polish_acceptance import descendants, open_menu

OUTPUT = Path("build/tissue-intersection-policy/ui")


def narrow(window):
    window.resize(1050, 900)
    pane = find(window, "inspector").parentItem().parentItem()
    expression = QQmlExpression(
        QQmlEngine.contextForObject(pane), pane, "SplitView.preferredWidth=280"
    )
    expression.evaluate()
    assert not expression.hasError(), expression.error().toString()
    QTest.qWait(100)


def label_check(window, text):
    labels = [
        i
        for i in descendants(window.contentItem())
        if i.isVisible()
        and i.property("text") == text
        and i.metaObject().indexOfProperty("truncated") >= 0
    ]
    assert labels and not any(i.property("truncated") for i in labels), text


def screenshot(window, name):
    QTest.qWait(80)
    assert window.grabWindow().save(str(OUTPUT / (name + ".png")))


def popup_check(window):
    combo = find(window, "surfaceSourceChoice")
    reveal(window, "surfaceSourceChoice")
    click(window, "surfaceSourceChoice")
    popup = combo.findChild(QObject, "comboPopup")
    QTest.qWait(100)
    labels = [
        i
        for i in descendants(popup.property("contentItem"))
        if i.isVisible() and i.metaObject().indexOfProperty("truncated") >= 0
    ]
    assert labels and not any(i.property("truncated") for i in labels)
    assert popup.property("width") > combo.width()
    screenshot(window, "complete-source-choices")
    QMetaObject.invokeMethod(popup, "close", Qt.DirectConnection)


def surface(controller, window):
    scene(controller)
    source = controller.session.document.object(controller.selection).curves[0].curve
    controller.run(
        "object.rename",
        dict(target=source, name="Left clavicle attachment and outer membrane boundary"),
    )
    settle(controller)
    narrow(window)
    label_check(window, "Across strips · 0 keeps fitted density")
    screenshot(window, "surface-labels")
    popup_check(window)
    controller.select(source)
    controller.authoring.setEditing(True)
    settle(controller)


def inspect(controller, window):
    for name in ("viewX", "viewY", "viewZ", "restoreView", "measureSurface", "xrayToggle"):
        label_check(window, find(window, name).property("text"))
    surface(controller, window)
    label_check(window, "Curve evaluation resolution")
    screenshot(window, "curve-labels")
    menu = open_menu(window, "Help")
    labels = [
        i
        for i in descendants(menu.property("contentItem"))
        if i.metaObject().indexOfProperty("truncated") >= 0
    ]
    assert labels and not any(i.property("truncated") for i in labels)
    screenshot(window, "help-menu")


def fonts(app):
    for family in ("Segoe UI", "Arial", "Tahoma"):
        app.setFont(QFont(family))
        run(inspect)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            fonts(app)
            print("Narrow surface/curve labels, source choices and Help menu passed.")
        finally:
            delete(app)


if __name__ == "__main__":
    main()
