"""Full Main-window shortcut gestures, driven fields and Parametric rendering offscreen."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

import json
from pathlib import Path

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import find

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/shortcuts-workflow-review").resolve()


def settle(controller):
    controller.session.wait(10)
    controller.refresh()
    QTest.qWait(150)
    assert not controller.session.scheduler.errors, controller.session.scheduler.errors


def fixture(controller):
    session = controller.session
    curve = create_curve(session)
    session.wait(5)
    body = session.command("primitive.from_curves", curves=[curve], kind="BODY")
    driver = create_driver(session, curve)
    settle(controller)
    controller.select(body)
    controller.cameraRequested.emit([0, 0, 0.1, 0, 0, 0, 1.2], True)
    return curve, body, driver


def create_curve(session):
    return session.command(
        "curve.create",
        engine="PARAMETRIC",
        settings=dict(
            x="radius*cos(t)",
            y="radius*sin(t)",
            z="t*0.04*m",
            resolution=48,
            interval=dict(end=4.5),
            variables=[dict(name="radius", value=0.25, dimension="LENGTH")],
        ),
    )


def create_driver(session, curve):
    variable = session.document.object(curve).engine_settings.variables[0].id
    ref = dict(target=curve, path=["engine_settings", "variables", "@" + variable, "value"])
    driver = session.command("driver.create", label="Arc radius", value=0.25, dimension="LENGTH")
    session.command("driver.formula.add", driver=driver, target=ref, expression="value")
    return driver


def show_shortcuts(controller, window):
    find(window, "inspectorHeader").setProperty("shortcuts", True)
    settle(controller)
    assert controller.shortcut_panel.model.rowCount() == 1
    assert not window.property("modalOpen")


def scrub(controller, window, driver, cancel=False):
    field = find(window, "shortcutValue" + driver + ":0")
    start = field.mapToScene(QPointF(field.width() / 2, field.height() / 2)).toPoint()
    QTest.mousePress(window, Qt.LeftButton, pos=start)
    for step in (20, 35, 50):
        QTest.mouseMove(window, start + QPoint(step, 0), 30)
        settle(controller)
        assert field.property("scrubbing") and field.hasActiveFocus()
    if cancel:
        QTest.keyClick(window, Qt.Key_Escape)
    QTest.mouseRelease(window, Qt.LeftButton, pos=start + QPoint(50, 0))
    settle(controller)


def gesture_checks(controller, window, curve, driver):
    document, cursor = controller.session.document, controller.session.history.cursor
    scrub(controller, window, driver)
    assert controller.session.history.cursor == cursor + 1
    assert controller.session.document.object(curve).engine_settings.variables[0].value > 0.25
    assert window.grabWindow().save(str(OUTPUT / "shortcuts.png"))
    controller.run("undo", {})
    settle(controller)
    assert_settings(controller, curve, document)
    cursor = controller.session.history.cursor
    scrub(controller, window, driver, cancel=True)
    assert controller.session.history.cursor == cursor
    assert_settings(controller, curve, document)


def assert_settings(controller, curve, document):
    assert (
        controller.session.document.object(curve).engine_settings
        == document.object(curve).engine_settings
    )


def exercise(controller, window):
    curve, body, driver = fixture(controller)
    show_shortcuts(controller, window)
    controller.profile_controls.toggle()
    gesture_checks(controller, window, curve, driver)
    controller.profile_controls.toggle()
    controller.select(curve)
    controller.authoring.setEditing(True)
    find(window, "inspectorHeader").setProperty("shortcuts", False)
    settle(controller)
    reveal_equations(window)
    assert window.grabWindow().save(str(OUTPUT / "parametric.png"))
    assert controller.session.document.entity(body).result.status == "ready"


def reveal_equations(window):
    from numeric_input_acceptance import reveal

    reveal(window, "parametricExpressionx")


def run():
    profiler, controller, warnings = QtProfiler(), Controller(), []
    controller.capture_mode, controller.qt_profiler = True, profiler
    engine = create_engine(controller, warnings)
    try:
        exercise(controller, engine.rootObjects()[0])
        assert not warnings, warnings
        (OUTPUT / "acceptance.json").write_text(json.dumps(dict(passed=True, interactive=False)))
    finally:
        controller.close()
        delete(engine)
        profiler.close()


if __name__ == "__main__":
    from anthroforge.profiling import report

    OUTPUT.mkdir(parents=True, exist_ok=True)
    report.default_directory = lambda: OUTPUT
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        application = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        application.setFont(QFont("Segoe UI"))
        try:
            run()
        finally:
            delete(application)
    print("Full-window shortcut gestures, undo/cancel and Parametric scene checks passed.")
