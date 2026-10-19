"""Development desktop entry point with explicit, bounded smoke mode."""

import argparse
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from anthroforge import __version__
from anthroforge.desktop import smoke
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.input_state import InputState
from anthroforge.desktop.runtime import build_directory, native_runtime


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="anthroforge-desktop")
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--smoke-panel", choices=("activity", "issues"), default="")
    parser.add_argument("--screenshot")
    parser.add_argument("--project")
    parser.add_argument("--disable-profiling-support", action="store_true")
    parser.add_argument("--profile-probe")
    parser.add_argument("--feedback-probe")
    return parser.parse_args()


def create_engine(controller: Controller, warnings: list[str]) -> QQmlApplicationEngine:
    QGuiApplication.setApplicationVersion(__version__)
    engine = QQmlApplicationEngine()
    engine.addImportPath(str(build_directory() / "qml"))
    engine.rootContext().setContextProperty("workspace", controller)
    engine.rootContext().setContextProperty("authoring", controller.authoring)
    setup_profile_controls(controller, engine)
    inputs = InputState(engine)
    engine.rootContext().setContextProperty("heldInput", inputs)
    engine.warnings.connect(lambda errors: warnings.extend(error.toString() for error in errors))
    engine.load(QUrl.fromLocalFile(str(Path(__file__).parent / "qml" / "Main.qml")))
    attach_window(engine, controller, inputs)
    return engine


def attach_window(engine, controller, inputs):
    if not engine.rootObjects():
        return
    window = engine.rootObjects()[0]
    window.frameSwapped.connect(controller.frame_presented)
    window.installEventFilter(inputs)
    if getattr(controller, "qt_profiler", None):
        controller.qt_profiler.attach(window, controller)


def setup_profile_controls(controller, engine):
    from .profile_controls import ProfileControls

    controller.profile_controls = ProfileControls(
        controller, getattr(controller, "qt_profiler", None)
    )
    engine.rootContext().setContextProperty("performance", controller.profile_controls)
    setup_feedback_controls(controller, engine)


def setup_feedback_controls(controller, engine):
    from .feedback_canvas import FeedbackCanvas
    from .feedback_editor import FeedbackEditor

    assert FeedbackCanvas  # Import registers the QML-painted annotation component.
    controller.feedback = FeedbackEditor(controller)
    engine.rootContext().setContextProperty("feedback", controller.feedback)


def launch(args: argparse.Namespace, app: QGuiApplication, profiler=None) -> int:
    controller, warnings = open_controller(args.project), []
    controller.qt_profiler = profiler
    app.aboutToQuit.connect(controller.close)
    engine = create_engine(controller, warnings)
    prepare_view(controller, args.project)
    if not engine.rootObjects():
        print("Cannot load desktop; run tools/setup.ps1 and inspect QML errors.", file=sys.stderr)
        print("\n".join(warnings), file=sys.stderr)
        return 1
    schedule_diagnostics(args, app, engine, controller, warnings)
    return app.exec()


def schedule_diagnostics(args, app, engine, controller, warnings):
    if args.smoke_test:
        smoke.schedule(app, engine, args.screenshot, warnings, args.smoke_panel, controller)
    if args.profile_probe:
        from .profile_probe import ProfileProbe

        ProfileProbe(app, controller, args.profile_probe)
    if args.feedback_probe:
        from .feedback_probe import FeedbackProbe

        FeedbackProbe(app, controller, engine, args.feedback_probe)


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
    with native_runtime():
        return run_application(args)


def run_application(args):
    from shiboken6 import delete

    from .qt_profiler import profiler_application

    app = profiler_application()
    app.setApplicationName("AnthroForge")
    try:
        return profiled_launch(args, app)
    finally:
        delete(app)


def profiled_launch(args, app):
    from .qt_profiler import QtProfiler

    profiler = None if args.disable_profiling_support else QtProfiler()
    try:
        return launch(args, app, profiler)
    finally:
        if profiler:
            profiler.close()


if __name__ == "__main__":
    raise SystemExit(main())
