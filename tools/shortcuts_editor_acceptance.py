"""Offscreen production shortcut/Parametric editors; excludes the native viewport."""

from math import isclose, pi
from pathlib import Path

from PySide6.QtCore import Q_ARG, QMetaObject, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from ui_acceptance import find

from anthroforge.desktop import app
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.property_projection import PropertyProjection

OUTPUT = Path("build/shortcuts-editor-review").resolve()
QML = b"""
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
ApplicationWindow {
    visible: true; width: 900; height: 820; color: Theme.panel
    RowLayout {
        anchors.fill: parent; anchors.margins: 16; spacing: 24
        Shortcuts { allObjects: true; Layout.fillHeight: true; Layout.preferredWidth: 420 }
        ParametricInspector {
            curve: probeCurve; Layout.preferredWidth: 420; Layout.alignment: Qt.AlignTop
        }
    }
}
"""


def settle(controller):
    controller.session.wait(5)
    controller.refresh()
    QTest.qWait(80)
    assert not controller.session.scheduler.errors, controller.session.scheduler.errors


def parametric_curve(session):
    return session.command(
        "curve.create",
        engine="PARAMETRIC",
        settings=dict(variables=[dict(name="radius", dimension="LENGTH", value=0.3)]),
    )


def prepare(controller):
    session = controller.session
    session.command("workspace.update", display_units="mm")
    curve = parametric_curve(session)
    driver = session.command(
        "driver.create", label="Length control", dimension="LENGTH", value=0.25
    )
    reference = dict(target=curve, path=["engine_settings", "resolution"])
    formula = session.command("driver.formula.add", driver=driver, target=reference, expression="8")
    settle(controller)
    controller.shortcut_panel.editor.select(driver)
    return curve, driver, formula


def create_engine(controller, curve, warnings):
    engine = QQmlApplicationEngine()
    context = engine.rootContext()
    context.setContextProperty("workspace", controller)
    context.setContextProperty("authoring", controller.authoring)
    context.setContextProperty("numericEdits", controller.numeric_edits)
    engine.probe_curve = PropertyProjection(engine)
    engine.probe_curve.synchronize(controller.session.document.object(curve))
    context.setContextProperty("probeCurve", engine.probe_curve)
    engine.warnings.connect(lambda errors: warnings.extend(error.toString() for error in errors))
    engine.loadData(QML, QUrl.fromLocalFile(str(Path(app.__file__).parent / "qml" / "Probe.qml")))
    assert engine.rootObjects(), warnings
    QTest.qWait(100)
    return engine


def edit(field, text):
    assert QMetaObject.invokeMethod(field, "beginText")
    field.setProperty("text", text)
    assert QMetaObject.invokeMethod(field, "commitText")


def driver_units(controller, window, driver):
    field = find(window, "driverValue")
    assert field.property("text") == "250.0000"
    assert field.property("unitLabel") == "mm"
    edit(field, "400")
    settle(controller)
    assert controller.shortcut_panel.editor.details["value"] == 0.4
    controller.run(
        "driver.configure", dict(driver=driver, changes=dict(dimension="ANGLE", value=pi / 2))
    )
    settle(controller)
    assert field.property("text") == "90.0000" and field.property("unitLabel") == "°"
    edit(field, "180")
    settle(controller)
    assert isclose(controller.shortcut_panel.editor.details["value"], pi)


def variable_units(controller, engine, window, curve):
    variable = controller.session.document.object(curve).engine_settings.variables[0]
    field = find(window, "parametricVariable" + variable.id)
    assert field.property("text") == "300.0000"
    edit(field, "2000")
    settle(controller)
    assert controller.session.document.object(curve).engine_settings.variables[0].value == 2
    engine.probe_curve.synchronize(controller.session.document.object(curve))
    QTest.qWait(80)
    variable_type(controller, window, curve, variable.id)
    engine.probe_curve.synchronize(controller.session.document.object(curve))


def variable_type(controller, window, curve, variable):
    choice = find(window, "parametricVariableType" + variable)
    choice.setProperty("currentIndex", 1)
    assert QMetaObject.invokeMethod(choice, "activated", Q_ARG(int, 1))
    settle(controller)
    assert (
        controller.session.document.object(curve).engine_settings.variables[0].numeric_type
        == "INTEGER"
    )


def field_navigation(controller, window, curve, driver):
    reference = dict(target=curve, path=["engine_settings", "resolution"])
    panel = controller.shortcut_panel
    assert not panel.propertyState(reference, 0)["writable"]
    field = find(window, "parametricResolutionValue")
    assert field.isVisible()
    assert field.property("propertyLocked")
    assert QMetaObject.invokeMethod(field, "beginText")
    assert not field.property("textEditing")
    panel.editor.select("")
    panel.openDriver(reference)
    assert panel.editor.key == driver


def exercise(controller, engine, curve, driver, warnings):
    window = engine.rootObjects()[0]
    driver_units(controller, window, driver)
    variable_units(controller, engine, window, curve)
    field_navigation(controller, window, curve, driver)
    resolution_membership(controller, window, curve, driver)
    QTest.qWait(100)
    assert window.grabWindow().save(str(OUTPUT / "editors.png"))
    controller.shortcut_panel.editor.select("")
    QTest.qWait(100)
    assert window.grabWindow().save(str(OUTPUT / "shortcut-list.png"))
    assert not warnings, warnings


def restricted_binding(controller, curve):
    session = controller.session
    body = session.command("primitive.from_curves", curves=[curve], kind="BODY")
    settle(controller)
    control = session.command("control.create", entity=body)
    return session.command(
        "deformer.add",
        control=control,
        target=dict(owner=body, stage="CURVE", component=curve),
        indices=[0, 1, 2],
    )


def resolution_membership(controller, window, curve, driver):
    controller.session.command("driver.remove", driver=driver)
    binding = restricted_binding(controller, curve)
    settle(controller)
    field, setting = find(window, "parametricResolutionValue"), find(window, "parametricResolution")
    assert field.property("propertyLocked") and "membership" in setting.property("hint")
    assert QMetaObject.invokeMethod(field, "beginText") and not field.property("textEditing")
    assert window.grabWindow().save(str(OUTPUT / "resolution-locked.png"))
    controller.session.command("deformer.remove", binding=binding)
    settle(controller)
    assert not field.property("propertyLocked")
    edit(field, "12")
    settle(controller)
    assert controller.session.document.object(curve).engine_settings.resolution == 12


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    application = QGuiApplication([])
    controller = Controller()
    warnings = []
    try:
        curve, driver, _ = prepare(controller)
        engine = create_engine(controller, curve, warnings)
        exercise(controller, engine, curve, driver, warnings)
        engine.rootObjects()[0].close()
    finally:
        controller.timer.stop()
        controller.session.close()
    assert application


if __name__ == "__main__":
    main()
    print("Offscreen shortcut units, Parametric variable type and driver navigation passed.")
