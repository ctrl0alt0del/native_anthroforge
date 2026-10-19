"""Window capture, annotation, delivery and keyboard acceptance; strictly offscreen."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
if os.name == "nt":
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ["SystemRoot"], "Fonts"))

import json
import sys
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from PySide6.QtCore import QMetaObject, QPointF, Qt
from PySide6.QtGui import QImage
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import click, find

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime
from anthroforge.feedback.storage import LocalReportConsumer

OUTPUT = Path(sys.argv[1] if len(sys.argv) > 1 else "build/feedback-acceptance").resolve()


def wait_for(predicate):
    for _ in range(400):
        if predicate():
            return
        QTest.qWait(25)
    raise AssertionError("Timed out waiting for feedback state")


def start(window, controller):
    find(window, "outlinerSearch").forceActiveFocus()
    before = window.grabWindow()
    QTest.keyClick(window, Qt.Key_F12)
    wait_for(lambda: find(window, "feedbackDialog").property("visible"))
    assert not controller.profiler.active
    source = controller.feedback.image
    assert source.size() == before.size() and source.devicePixelRatio() == 1
    assert source.copy(420, 220, 160, 160) == before.copy(420, 220, 160, 160)
    assert window.property("modalOpen")
    return controller.feedback.id


def source_point(window, x, y):
    canvas = find(window, "feedbackCanvas")
    area, _ = canvas.placement()
    point = QPointF(area.x() + x * area.width(), area.y() + y * area.height())
    return canvas.mapToScene(point).toPoint()


def drag(window, start, end):
    QTest.mousePress(window, Qt.LeftButton, pos=source_point(window, *start))
    QTest.mouseMove(window, source_point(window, *end), delay=30)
    QTest.mouseRelease(window, Qt.LeftButton, pos=source_point(window, *end))
    QTest.qWait(60)


def annotations(window, controller):
    zoom_alignment(window, controller)
    click(window, "feedbackTool_rectangle")
    drag(window, (0.15, 0.20), (0.45, 0.45))
    click(window, "feedbackTool_arrow")
    drag(window, (0.7, 0.7), (0.4, 0.35))
    click(window, "feedbackTool_text")
    find(window, "feedbackAnnotationText").setProperty("text", "Inspect this area →")
    QTest.mouseClick(window, Qt.LeftButton, pos=source_point(window, 0.18, 0.55))
    QTest.qWait(60)
    assert [a.kind for a in controller.feedback.annotations] == ["rectangle", "arrow", "text"]
    mark = controller.feedback.annotations[0]
    assert abs(mark.x1 / controller.feedback.image.width() - 0.15) < 0.005
    assert abs(mark.y2 / controller.feedback.image.height() - 0.45) < 0.005
    undo_mark(window, controller)


def zoom_alignment(window, controller):
    zoom = find(window, "feedbackZoom")
    zoom.setProperty("currentIndex", 1)
    QTest.qWait(80)
    assert abs(find(window, "feedbackCanvas").placement()[1] - 1) < 1e-6
    zoom_mark(window, controller)
    zoom.setProperty("currentIndex", 0)
    QTest.qWait(80)
    assert find(window, "feedbackCanvas").placement()[1] < 1
    assert not controller.feedback.annotations


def zoom_mark(window, controller):
    view = find(window, "feedbackImageView")
    view.setProperty("contentX", 150)
    view.setProperty("contentY", 80)
    image = controller.feedback.image
    drag(
        window,
        (300 / image.width(), 180 / image.height()),
        (500 / image.width(), 280 / image.height()),
    )
    mark = controller.feedback.annotations[0]
    assert abs(mark.x1 - 300) < 2 and abs(mark.y2 - 280) < 2
    click(window, "feedbackUndo")
    view.setProperty("contentX", 0)
    view.setProperty("contentY", 0)


def undo_mark(window, controller):
    click(window, "feedbackUndo")
    assert len(controller.feedback.annotations) == 2
    QTest.mouseClick(window, Qt.LeftButton, pos=source_point(window, 0.18, 0.55))
    assert len(controller.feedback.annotations) == 3


def submit_failure_retry(window, controller):
    blocked = OUTPUT / "not-a-directory"
    blocked.write_text("Preserve this file")
    consumer = LocalReportConsumer(blocked)
    controller.feedback.service.consumer = consumer
    find(window, "feedbackDescription").setProperty("text", "Recommendation: inspect marked area.")
    find(window, "feedbackCategory").setProperty("currentIndex", 1)
    assert window.grabWindow().save(str(OUTPUT / "editor.png"))
    click(window, "feedbackSubmit")
    wait_for(lambda: controller.feedback.service.state == "failed")
    assert controller.feedback.state["error"] and len(controller.feedback.annotations) == 3
    consumer.directory = OUTPUT / "inbox"
    click(window, "feedbackSubmit")
    wait_for(lambda: controller.feedback.service.state == "saved")


def verify_archive(controller, key):
    path = Path(controller.feedback.service.location)
    with ZipFile(path) as archive:
        data = json.loads(archive.read("report.json"))
        assert data["report_id"] == key and data["category"] == "recommendation"
        assert data["description"] == "Recommendation: inspect marked area."
        assert len(data["annotations"]) == 3 and len(archive.namelist()) == 4
        source = QImage.fromData(archive.read("original.png"))
        annotated = QImage.fromData(archive.read("annotated.png"))
    assert source == controller.feedback.image and source.size() == annotated.size()
    assert red_pixels(annotated) - red_pixels(source) > 1500
    assert annotated.save(str(OUTPUT / "annotated.png"))
    return data


def red_pixels(image):
    rgba = image.convertToFormat(QImage.Format_RGBA8888)
    pixels = np.frombuffer(rgba.constBits(), np.uint8).reshape(rgba.height(), rgba.width(), 4)
    return int(((pixels[:, :, 0] > 200) & (pixels[:, :, 1] < 100)).sum())


def menu_cancel(window, controller):
    click(window, "feedbackCancel")
    menu = find(window, "helpMenu")
    assert QMetaObject.invokeMethod(menu, "open", Qt.DirectConnection)
    QTest.qWait(80)
    click(window, "reportFeedbackMenu")
    wait_for(lambda: find(window, "feedbackDialog").property("visible"))
    assert not menu.property("visible")
    click(window, "feedbackCancel")
    assert not controller.feedback.active and controller.feedback.image.isNull()
    assert len(list((OUTPUT / "inbox").glob("*.afreport.zip"))) == 1


def report_modal(window, controller):
    help_dialog = find(window, "shortcutHelp")
    assert QMetaObject.invokeMethod(help_dialog, "open", Qt.DirectConnection)
    QTest.qWait(80)
    QTest.keyClick(window, Qt.Key_F12)
    wait_for(lambda: find(window, "feedbackDialog").property("visible"))
    key = controller.feedback.id
    QTest.keyClick(window, Qt.Key_F12)
    assert controller.feedback.id == key
    click(window, "feedbackCancel")
    assert help_dialog.property("visible")
    assert QMetaObject.invokeMethod(help_dialog, "close", Qt.DirectConnection)
    QTest.qWait(80)


def capture_failure(controller):
    from types import SimpleNamespace

    controller.feedback.capture(SimpleNamespace(grabWindow=lambda: QImage()))
    assert (
        controller.state["message"] == controller.message
        and "Screenshot failed" in controller.message
    )
    assert not controller.feedback.active and controller.feedback.image.isNull()
    controller.message = ""
    controller.notify()


def profiling_shortcut(window, controller):
    from anthroforge.profiling import report

    report.default_directory = lambda: OUTPUT
    QTest.keyClick(window, Qt.Key_F12, Qt.ControlModifier | Qt.ShiftModifier)
    assert controller.profiler.active and not controller.feedback.active
    QTest.keyClick(window, Qt.Key_F12, Qt.ShiftModifier)
    wait_for(lambda: controller.profiler.done.is_set())
    assert controller.profiler.state == "saved"


def exercise(window, controller):
    before, cursor = controller.session.document, controller.session.history.cursor
    key = start(window, controller)
    annotations(window, controller)
    submit_failure_retry(window, controller)
    data = verify_archive(controller, key)
    menu_cancel(window, controller)
    report_modal(window, controller)
    capture_failure(controller)
    profiling_shortcut(window, controller)
    assert controller.session.document is before and controller.session.history.cursor == cursor
    (OUTPUT / "acceptance.json").write_text(json.dumps(data, indent=2))


def test_engine(controller, warnings):
    engine = create_engine(controller, warnings)
    if engine.rootObjects() and "--small" in sys.argv:
        engine.rootObjects()[0].resize(1050, 680)
    return engine


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    profiler, controller, warnings = QtProfiler(), open_controller(None), []
    controller.qt_profiler, controller.capture_mode = profiler, True
    engine = test_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        QTest.qWait(200)
        exercise(engine.rootObjects()[0], controller)
        assert not warnings, warnings
        print("Feedback capture, annotations, failure/retry, cancel and shortcuts passed.")
    finally:
        controller.close()
        delete(engine)
        profiler.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run()
        finally:
            delete(app)
