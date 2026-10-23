"""Exercise exact int64 editing, scrubbing and undo through production QML controls."""

from pathlib import Path

from PySide6.QtCore import Q_ARG, QMetaObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shortcuts_editor_acceptance import create_engine, edit, prepare, settle
from ui_acceptance import find

from anthroforge.desktop.controller import Controller

BASE = 9007199254740993
OUTPUT = Path("build/shortcuts-editor-review")


def integer_driver(controller):
    curve, driver, formula = prepare(controller)
    controller.session.command(
        "driver.configure",
        driver=driver,
        changes=dict(numeric_type="INTEGER", dimension="SCALAR", value=BASE),
    )
    controller.session.command(
        "driver.formula.update",
        driver=driver,
        formula=formula,
        changes=dict(expression="value - 9007199254740990"),
    )
    settle(controller)
    return curve, driver, formula


def assert_driver(controller, curve, expected):
    settle(controller)
    assert controller.shortcut_panel.editor.details["value"] == expected
    assert (
        controller.session.document.object(curve).engine_settings.resolution == expected - BASE + 3
    )


def driver_edit(controller, window, curve):
    field = find(window, "driverValue")
    assert field.property("text") == str(BASE)
    edit(field, str(BASE + 2))
    assert_driver(controller, curve, BASE + 2)
    cursor = controller.session.history.cursor
    assert QMetaObject.invokeMethod(field, "beginScrub")
    assert controller.numeric_edits.active
    assert QMetaObject.invokeMethod(field, "updateScrub", Q_ARG("QVariant", 7))
    assert QMetaObject.invokeMethod(field, "updateScrub", Q_ARG("QVariant", 17))
    assert QMetaObject.invokeMethod(field, "finishScrub")
    assert_driver(controller, curve, BASE + 19)
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    assert_driver(controller, curve, BASE + 2)


def list_edit(controller, window, curve, driver):
    controller.shortcut_panel.editor.select("")
    QTest.qWait(80)
    field = find(window, "shortcutValue" + driver + ":0")
    assert field.isVisible() and field.property("text") == str(BASE + 2)
    edit(field, str(BASE + 4))
    controller.shortcut_panel.editor.select(driver)
    assert_driver(controller, curve, BASE + 4)


def variable_edit(controller, engine, curve):
    session = controller.session
    variable = session.command(
        "curve.parametric.variable.add", curve=curve, name="n", numeric_type="INTEGER", value=BASE
    )
    settle(controller)
    engine.probe_curve.synchronize(session.document.object(curve))
    QTest.qWait(80)
    field = find(engine.rootObjects()[0], "parametricVariable" + variable)
    assert field.property("text") == str(BASE)
    edit(field, str(BASE + 6))
    settle(controller)
    assert session.document.object(curve).engine_settings.variables[-1].value == BASE + 6
    return variable


def retain_integer_type(controller, engine, curve, variable):
    engine.probe_curve.synchronize(controller.session.document.object(curve))
    QTest.qWait(80)
    combo = find(engine.rootObjects()[0], "parametricVariableType" + variable)
    assert QMetaObject.invokeMethod(combo, "activated", Q_ARG(int, 1))
    settle(controller)
    assert controller.session.document.object(curve).engine_settings.variables[-1].value == BASE + 6


def exercise(controller, engine, curve, driver, warnings):
    window = engine.rootObjects()[0]
    driver_edit(controller, window, curve)
    list_edit(controller, window, curve, driver)
    variable = variable_edit(controller, engine, curve)
    retain_integer_type(controller, engine, curve, variable)
    assert window.grabWindow().save(str(OUTPUT / "integer-editors.png"))
    assert not warnings, warnings


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    application = QGuiApplication([])
    controller, warnings = Controller(), []
    try:
        curve, driver, _ = integer_driver(controller)
        engine = create_engine(controller, curve, warnings)
        exercise(controller, engine, curve, driver, warnings)
        engine.rootObjects()[0].close()
    finally:
        controller.timer.stop()
        controller.session.close()
    assert application


if __name__ == "__main__":
    main()
    print("Exact integer driver/list/variable edits, native outputs and scrub undo passed.")
