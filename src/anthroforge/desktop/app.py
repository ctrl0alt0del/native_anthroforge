"""Development desktop entry point with explicit, bounded smoke mode."""

import argparse
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from anthroforge.desktop import smoke
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.input_state import InputState
from anthroforge.desktop.runtime import build_directory, native_runtime


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="anthroforge-desktop")
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--screenshot")
    parser.add_argument("--project")
    return parser.parse_args()


def create_engine(controller: Controller, warnings: list[str]) -> QQmlApplicationEngine:
    engine = QQmlApplicationEngine()
    engine.addImportPath(str(build_directory() / "qml"))
    engine.rootContext().setContextProperty("workspace", controller)
    engine.rootContext().setContextProperty("authoring", controller.authoring)
    inputs = InputState(engine)
    engine.rootContext().setContextProperty("heldInput", inputs)
    engine.warnings.connect(lambda errors: warnings.extend(error.toString() for error in errors))
    engine.load(QUrl.fromLocalFile(str(Path(__file__).parent / "qml" / "Main.qml")))
    if engine.rootObjects():
        engine.rootObjects()[0].frameSwapped.connect(controller.frame_presented)
        engine.rootObjects()[0].installEventFilter(inputs)
    return engine


def launch(args: argparse.Namespace, app: QGuiApplication) -> int:
    controller, warnings = open_controller(args.project), []
    app.aboutToQuit.connect(controller.close)
    engine = create_engine(controller, warnings)
    prepare_view(controller, args.project)
    if not engine.rootObjects():
        print("Cannot load desktop; run tools/setup.ps1 and inspect QML errors.", file=sys.stderr)
        print("\n".join(warnings), file=sys.stderr)
        return 1
    if args.smoke_test:
        smoke.schedule(app, engine, args.screenshot, warnings)
    return app.exec()


def open_controller(project):
    controller = Controller()
    if project:
        controller.session.command("open", path=project)
        controller.session.command("wait")
        controller.refresh()
    return controller


def prepare_view(controller, project):
    controller.camera_workspace = None
    controller.restore_camera()
    if project and controller.session.document.entities:
        controller.select(controller.session.document.entities[0].id)
        if controller.session.workspace.camera == (0.0, 0.0, 0.0, -20.0, 25.0, 0.0, 4.0):
            QTimer.singleShot(100, controller.frameSelection)


def main() -> int:
    args = arguments()
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([sys.argv[0]])
    app.setApplicationName("AnthroForge")
    with native_runtime():
        return launch(args, app)


if __name__ == "__main__":
    raise SystemExit(main())
