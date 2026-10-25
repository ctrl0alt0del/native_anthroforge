"""Background checks of shared tooltips and explicit OS actions; never opens desktop apps."""

import json
import os
from pathlib import Path
from unittest.mock import patch

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import QPointF
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtQml import QQmlEngine, QQmlExpression
from PySide6.QtTest import QTest
from ui_acceptance import click, find
from usability_037_acceptance import findings, invoke

from anthroforge.desktop import windows_associations
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime
from anthroforge.desktop.style import configure

OUTPUT = Path("build/preferences-ui-design/ui").resolve()
REGISTER = "anthroforge.desktop.windows_associations.register"
OPEN_URL = "anthroforge.desktop.system_integration.QDesktopServices.openUrl"
MESSAGES = (
    "Open autosave folder",
    "Choose how fibers follow their supports. Smooth Shape Preservation spreads support motion "
    "while retaining the curve's shape and exact attachment points. Current results stay "
    "unchanged until the next calculation.",
    "Open .anthroforge projects from File Explorer.\nChoose AnthroForge in Windows Default Apps.",
    "E:/" + "long-folder-name/" * 25 + "project.anthroforge",
)


def evaluate(item, expression):
    evaluator = QQmlExpression(QQmlEngine.contextForObject(item), item, expression)
    result, _ = evaluator.evaluate()
    assert not evaluator.hasError(), evaluator.error().toString()
    return result


def tooltip(window, item, text, name):
    item.setProperty("hint", text)
    evaluate(item, "ToolTip.show(hint, 60000)")
    QTest.qWait(600)
    tip = evaluate(item, "ToolTip.toolTip")
    assert tip.objectName() == "applicationToolTip" and tip.property("visible"), tip
    content = tip.property("contentItem")
    assert tip.property("width") <= 380 and content.property("lineCount") >= 1
    assert content.property("contentWidth") <= content.width() + 1
    assert window.grabWindow().save(str(OUTPUT / (name + ".png")))
    record = dict(width=tip.property("width"), lines=content.property("lineCount"))
    evaluate(item, "ToolTip.hide()")
    return record


def tooltips(window, report):
    item = find(window, "preferencesAutosaveFolder")
    for index, message in enumerate(MESSAGES):
        report[f"tooltip-{index}"] = tooltip(window, item, message, f"tooltip-{index}")
    assert report["tooltip-0"]["lines"] == 1
    assert all(report[f"tooltip-{i}"]["lines"] > 1 for i in (1, 2, 3))
    point = item.mapToScene(QPointF(item.width() / 2, item.height() / 2))
    QTest.mouseMove(window, QPointF(2, 2).toPoint())
    QTest.mouseMove(window, point.toPoint())
    QTest.qWait(700)
    assert evaluate(item, "ToolTip.toolTip.visible")
    QTest.mouseMove(window, QPointF(2, 2).toPoint())
    QTest.qWait(80)
    assert not evaluate(item, "ToolTip.toolTip.visible")


def folder_actions(controller, window):
    browser = controller.project_library.recovery_browser
    with patch(
        "anthroforge.desktop.recovery_browser.QDesktopServices.openUrl", return_value=True
    ) as opened:
        click(window, "preferencesAutosaveFolder")
        assert Path(opened.call_args.args[0].toLocalFile()) == browser.store.directory
    with patch("anthroforge.desktop.recovery_browser.QDesktopServices.openUrl", return_value=False):
        browser.showFolder()
        assert "Could not open the autosave folder" in controller.message


def association_actions(controller, window):
    adapter = controller.system_integration
    assert not find(window, "preferencesFileAssociation").isEnabled()
    adapter.executable = OUTPUT / "Portable app" / "AnthroForge.exe"
    adapter.executable.parent.mkdir(exist_ok=True)
    adapter.executable.touch()
    with patch(REGISTER, return_value=windows_associations.SETTINGS) as registered:
        with patch(OPEN_URL, return_value=True) as opened:
            adapter.setupAssociation()
            registered.assert_called_once_with(adapter.executable)
            assert opened.call_args.args[0].toString() == windows_associations.SETTINGS
    assert "Windows Settings" in controller.message
    association_failure(controller)


def association_failure(controller):
    with patch(REGISTER, side_effect=PermissionError("Denied")):
        with patch(OPEN_URL) as opened:
            controller.system_integration.setupAssociation()
            opened.assert_not_called()
    assert controller.message == "Denied"
    with patch(REGISTER, return_value=windows_associations.SETTINGS):
        with patch(OPEN_URL, return_value=False):
            controller.system_integration.setupAssociation()
    assert "Default apps" in controller.message


def exercise(controller, engine, warnings):
    window, report = engine.rootObjects()[0], {}
    before = controller.session.document
    invoke(find(window, "preferencesMenu"), "triggered")
    for width, height in ((1440, 900), (1050, 680)):
        window.resize(width, height)
        QTest.qWait(200)
        assert not findings(window), findings(window)
        assert window.grabWindow().save(str(OUTPUT / f"preferences-{width}.png"))
    folder_actions(controller, window)
    association_actions(controller, window)
    tooltips(window, report)
    assert controller.session.document is before and not warnings, warnings
    (OUTPUT / "acceptance.json").write_text(json.dumps(report, indent=2))


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(OUTPUT / "state/preferences.json")
    configure()
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        controller, warnings = Controller(), []
        engine = create_engine(controller, warnings)
        try:
            exercise(controller, engine, warnings)
        finally:
            controller.close()
            engine.deleteLater()


if __name__ == "__main__":
    main()
