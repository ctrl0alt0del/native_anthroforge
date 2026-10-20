"""Real Qt keys/drags on production numeric widgets; run with QT_QPA_PLATFORM=offscreen."""

import json
from pathlib import Path

from primitive_acceptance import settle
from PySide6.QtCore import QLocale, QPoint, QPointF, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from ui_acceptance import find as find_any

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/outward-snap-numeric-fields")


def find(window, name):
    pending = [window.contentItem()]
    while pending:
        item = pending.pop()
        if item.objectName() == name and item.isVisible():
            return item
        pending.extend(item.childItems())
    return find_any(window, name)


def reveal(window, name):
    target = find(window, name)
    parent = target.parentItem()
    while parent and parent.metaObject().indexOfProperty("contentY") < 0:
        parent = parent.parentItem()
    if parent:
        offset = target.mapToItem(parent.property("contentItem"), QPointF()).y()
        parent.setProperty("contentY", max(0, offset - 60))
    QTest.qWait(100)


def type_value(window, name, value):
    reveal(window, name)
    field = find(window, name)
    center = field.mapToScene(QPointF(field.width() / 2, field.height() / 2)).toPoint()
    QTest.mouseClick(window, Qt.LeftButton, pos=center)
    QTest.keyClick(window, Qt.Key_A, Qt.ControlModifier)
    for character in value:
        QTest.keyClick(window, Qt.Key(ord(character)))
    assert field.property("text") == value, (name, field.property("text"))
    QTest.keyClick(window, Qt.Key_Return)
    QTest.qWait(50)
    return field


def drag(window, field, pixels, cancel=False):
    start = field.mapToScene(QPointF(field.width() / 2, field.height() / 2)).toPoint()
    QTest.mousePress(window, Qt.LeftButton, pos=start)
    for step in range(1, 5):
        QTest.mouseMove(window, start + QPoint(round(pixels * step / 4), 0), 20)
        QTest.qWait(20)
    if cancel:
        QTest.keyClick(window, Qt.Key_Escape)
    QTest.mouseRelease(window, Qt.LeftButton, pos=start + QPoint(pixels, 0))
    QTest.qWait(40)


def transform_checks(controller, window):
    target = controller.run("scp.empty", dict(name="Numeric input"))
    controller.select(target)
    for locale, text in (("uk_UA", "0.25"), ("ro_RO", "-0.125"), ("en_US", "0,5")):
        QLocale.setDefault(QLocale(locale))
        type_value(window, "transform0", text)
        assert controller.session.document.entity(target).matrix[3] == float(text.replace(",", "."))
    field = find(window, "transform0")
    transform_drag_checks(controller, window, target, field)


def transform_drag_checks(controller, window, target, field):
    before, cursor = controller.session.document, controller.session.history.cursor
    drag(window, field, 35)
    assert controller.session.history.cursor == cursor + 1
    assert controller.session.document.entity(target).matrix[3] > before.entity(target).matrix[3]
    controller.run("undo", {})
    assert controller.session.document.entity(target).matrix == before.entity(target).matrix
    drag(window, field, -35, cancel=True)
    assert controller.session.document.entity(target).matrix == before.entity(target).matrix


def primitive_checks(controller, window):
    target = controller.run("primitive.create", dict(kind="BODY", parent=controller.selection))
    assert target, controller.message
    controller.select(target)
    settle(controller)
    type_value(window, "primitiveSamplesValue", "36")
    assert controller.session.document.entity(target).primitive.samples == 36
    field = find(window, "primitiveSamplesValue")
    cursor = controller.session.history.cursor
    drag(window, field, 24)
    assert controller.session.document.entity(target).primitive.samples == 60
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    assert controller.session.document.entity(target).primitive.samples == 36


def verify(controller, window):
    window.resize(1500, 1000)
    QTest.qWait(200)
    transform_checks(controller, window)
    primitive_checks(controller, window)
    assert not controller.session.history.before
    assert window.grabWindow().save(str(OUTPUT / "numeric-fields.png"))
    return acceptance_flags()


def acceptance_flags():
    return dict(
        decimal_point=True,
        decimal_comma=True,
        locales=["uk_UA", "ro_RO", "en_US"],
        drag=True,
        integer_drag=True,
        one_undo=True,
        escape_cancel=True,
    )


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = open_controller(None), []
    controller.capture_mode = True
    engine = create_engine(controller, warnings)
    try:
        result = verify(controller, engine.rootObjects()[0])
        assert not warnings, warnings
        (OUTPUT / "numeric-acceptance.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result))
    finally:
        engine.rootObjects()[0].grabWindow().save(str(OUTPUT / "latest.png"))
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    QLocale.setDefault(QLocale("uk_UA"))
    app = QGuiApplication([])
    with native_runtime():
        run()
