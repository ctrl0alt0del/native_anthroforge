"""Background-only 0.4.2 view qualification; never shows a desktop window."""

import json
import os
from pathlib import Path

from PySide6.QtCore import QObject, QSizeF, QUrl
from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtQml import QQmlComponent
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from anthroforge.desktop import capture, offscreen, runtime
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.workbench_state import WorkbenchState

OUTPUT = Path("build/inspection-042")
QML = Path(__file__).resolve().parents[1] / "src/anthroforge/desktop/qml"


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(OUTPUT / "preferences.json")
    build = Path(os.environ.get("AF_NATIVE_BUILD", "build/dev")).resolve()
    runtime.build_directory = offscreen.build_directory = lambda: build
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with runtime.native_runtime():
        run(app)


def fixture(controller):
    session = controller.session
    target = session.command("import", path="examples/primitives/cube.obj", units=1)["entity_id"]
    session.wait()
    controller.refresh()
    controller.selection_view.select(target)
    return target


def run(app):
    controller, warnings = Controller(), []
    controller.timer.stop()
    controller.capture_mode = True
    target = fixture(controller)
    renderer = offscreen.Offscreen(controller, warnings)
    try:
        qualify(app, controller, renderer, target)
        inspector(app, controller, renderer)
        assert not renderer.window.isVisible() and not warnings, warnings
        (OUTPUT / "gui.json").write_text(json.dumps(dict(warnings=warnings, visible=False)))
    finally:
        renderer.close()
        controller.close()


def settle(app, controller, renderer, name):
    QTest.qWait(75)
    controller.session.wait()
    controller.process_tick()
    capture.stage_geometry(app, controller, renderer)
    for _ in range(4):
        app.processEvents()
        image = renderer.frame()
        controller.frame_presented()
    assert image.save(str(OUTPUT / (name + ".png")))


def qualify(app, controller, renderer, target):
    controller.viewport_view.frameSelection()
    controller.section_tools.enable(True)
    controller.section_tools.request()
    controller.surface_measurements.show(target, "final")
    controller.surface_measurements.submit()
    controller.surface_measurements.volumes.compare(target, "final", target, "SCP")
    settle(app, controller, renderer, "measurements")
    assert controller.surface_measurements.report["section"]["available"]
    before = controller.session.document
    controller.neighborhood.inspect()
    settle(app, controller, renderer, "neighborhood")
    controller.neighborhood.restore()
    assert controller.session.document is before
    placement(app, controller, renderer)


def placement(app, controller, renderer):
    controller.section_tools.cancel()
    controller.placement_inspection.toggle()
    controller.placement_inspection.probe([0, 0, 2], [0, 0, -1], True)
    settle(app, controller, renderer, "placement")
    assert controller.placement_inspection.report["confirmed"]["hit"]
    controller.placement_inspection.cancel()
    controller.inspection_panel.activate(True)


def inspector(app, controller, renderer):
    controller.workbench = WorkbenchState(controller, OUTPUT / "workbench.ini")
    for key in ("inspect/size", "inspect/placement"):
        controller.workbench.setExpanded(key, True)
    renderer.root.setVisible(False)
    renderer.window.setColor(QColor("#282a2d"))
    component = QQmlComponent(renderer.engine, QUrl.fromLocalFile(str(QML / "InspectionPane.qml")))
    panel = component.create()
    assert panel is not None, [e.toString() for e in component.errors()]
    panel.setParentItem(renderer.window.contentItem())
    panel.setSize(QSizeF(360, 960))
    settle(app, controller, renderer, "inspector")
    assert panel.findChild(QObject, "placementNormalDistance").property("value") == "1.5000 m"
    panel.deleteLater()


if __name__ == "__main__":
    main()
