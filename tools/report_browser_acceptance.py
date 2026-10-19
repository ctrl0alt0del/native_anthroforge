"""Actual QML inbox, bounded rows, previews and deletion, with an isolated report directory."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
if os.name == "nt":
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ["SystemRoot"], "Fonts"))

import sys
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import QEventLoop, QMetaObject, QPointF, Qt, QTimer
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import click, find

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.feedback_paint import annotated, png
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime
from anthroforge.feedback.local_inbox import LocalReportInbox
from anthroforge.feedback.records import Annotation, Report
from anthroforge.feedback.storage import LocalReportConsumer

OUTPUT = Path(sys.argv[1] if len(sys.argv) > 1 else "build/report-browser").resolve()


def wait_for(predicate):
    loop, check, deadline = QEventLoop(), QTimer(), QTimer()
    check.timeout.connect(lambda: loop.quit() if predicate() else None)
    deadline.timeout.connect(loop.quit)
    check.start(20)
    deadline.start(10000)
    loop.exec()  # Like the application, release the GIL while background archive I/O runs.
    check.stop()
    deadline.stop()
    assert predicate(), "Timed out waiting for report browser"


def seed(window):
    report = example_report(window.grabWindow())
    inbox = LocalReportConsumer(OUTPUT / "inbox")
    for index in range(120):
        inbox.submit(
            replace(report, id=uuid4().hex, description=f"Report {index:03} · {report.description}")
        )
    return LocalReportInbox(inbox.directory)


def example_report(image):
    marks = example_marks()
    return Report(
        uuid4().hex,
        "2026-10-19T12:30:00Z",
        "recommendation",
        "Curves: <b>literal text</b> · Україна\nPlease improve the selected tool.",
        "{}",
        image.width(),
        image.height(),
        marks,
        png(image),
        png(annotated(image, marks)),
    )


def example_marks():
    return (
        Annotation("rectangle", 80, 150, 360, 440),
        Annotation("text", 100, 180, 0, 0, "Review this area"),
    )


def open_browser(window, browser):
    menu = find(window, "helpMenu")
    assert QMetaObject.invokeMethod(menu, "open", Qt.DirectConnection)
    QTest.qWait(80)
    click(window, "viewReportsMenu")
    wait_for(lambda: not browser.state["busy"] and browser.state["count"] == 120)
    assert window.property("modalOpen") and not browser.image.isNull()
    assert "<b>literal text</b>" in find(window, "reportDescription").property("text")
    assert window.grabWindow().save(str(OUTPUT / "browser.png"))


def scroll_and_preview(window, browser):
    view = find(window, "reportsList")
    assert len(view.property("contentItem").childItems()) < 30
    view.setProperty("contentY", view.property("contentHeight") - view.height())
    QTest.qWait(100)
    point = view.mapToScene(QPointF(view.width() / 2, view.height() - 30)).toPoint()
    QTest.mouseClick(window, Qt.LeftButton, pos=point)
    wait_for(lambda: not browser.state["busy"])
    assert browser.key == browser.model.rows[-1]["key"]
    find(window, "reportsZoom").setProperty("currentIndex", 1)
    assert not browser.image.isNull()
    find(window, "reportsZoom").setProperty("currentIndex", 0)


def delete_report(window, browser):
    key = browser.key
    click(window, "reportsDelete")
    assert find(window, "reportDeleteConfirmation").property("visible")
    assert window.grabWindow().save(str(OUTPUT / "confirm.png"))
    click(window, "reportDeleteCancel")
    assert (browser.inbox.directory / key).exists() and browser.state["count"] == 120
    click(window, "reportsDelete")
    click(window, "reportDeleteConfirm")
    wait_for(lambda: not browser.state["busy"] and browser.state["count"] == 119)
    assert not (browser.inbox.directory / key).exists()
    assert not browser.image.isNull() and browser.key != key


class LockedInbox:
    def __init__(self, wrapped):
        self.entries, self.read = wrapped.entries, wrapped.read

    def delete(self, key):
        raise PermissionError("Test: report is locked")

    def update_description(self, key, description):
        raise PermissionError("Test: report is locked")


def failure_and_refresh(window, browser):
    inbox, key = browser.inbox, browser.key
    browser.inbox = LockedInbox(inbox)
    click(window, "reportsDelete")
    click(window, "reportDeleteConfirm")
    wait_for(lambda: not browser.state["busy"])
    assert "locked" in browser.state["error"] and (inbox.directory / key).exists()
    browser.inbox = inbox
    (inbox.directory / "corrupt.afreport.zip").write_bytes(b"not a report")
    click(window, "reportsRefresh")
    wait_for(lambda: not browser.state["busy"] and browser.state["count"] == 120)
    browser.select("corrupt.afreport.zip")
    wait_for(lambda: not browser.state["busy"])
    assert browser.state["error"] and browser.image.isNull()


def empty_and_close(window, browser):
    click(window, "reportsClose")
    assert not window.property("modalOpen") and browser.image.isNull()
    assert not browser.timer.isActive() and browser.model.rowCount() == 0
    browser.inbox = LocalReportInbox(OUTPUT / "empty")
    QMetaObject.invokeMethod(find(window, "reportBrowserDialog"), "open", Qt.DirectConnection)
    wait_for(lambda: not browser.state["busy"])
    assert browser.state["count"] == 0 and not find(window, "reportsDelete").property("enabled")
    assert window.grabWindow().save(str(OUTPUT / "empty.png"))
    click(window, "reportsClose")


def exercise(window, controller):
    browser = controller.report_browser
    before, cursor = controller.session.document, controller.session.history.cursor
    browser.inbox = seed(window)
    open_browser(window, browser)
    scroll_and_preview(window, browser)
    edit_description(window, browser)
    delete_report(window, browser)
    failure_and_refresh(window, browser)
    empty_and_close(window, browser)
    assert controller.session.document is before and controller.session.history.cursor == cursor


def edit_description(window, browser):
    previous, key, image = browser.description, browser.key, browser.image
    click(window, "reportEditText")
    find(window, "reportDescription").setProperty("text", "Discard this draft")
    click(window, "reportEditCancel")
    assert browser.inbox.read(key).description == previous
    click(window, "reportEditText")
    find(window, "reportDescription").setProperty("text", "Updated recommendation · Україна")
    edit_failure(window, browser)
    click(window, "reportEditSave")
    wait_for(lambda: not browser.state["busy"])
    assert browser.description == "Updated recommendation · Україна"
    assert browser.inbox.read(key).description == browser.description and browser.image == image
    assert not find(window, "reportBrowserDialog").property("editingDescription")


def edit_failure(window, browser):
    inbox = browser.inbox
    browser.inbox = LockedInbox(inbox)
    click(window, "reportEditSave")
    wait_for(lambda: not browser.state["busy"])
    assert "locked" in browser.state["error"]
    assert find(window, "reportBrowserDialog").property("editingDescription")
    assert find(window, "reportDescription").property("text") == "Updated recommendation · Україна"
    browser.inbox = inbox


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = open_controller(None), []
    engine = create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        window = prepare_window(engine)
        exercise(window, controller)
        assert not warnings, warnings
        print("Report browser: 120 rows, preview, delete/cancel/failure and empty state passed.")
    finally:
        controller.close()
        delete(engine)


def prepare_window(engine):
    window = engine.rootObjects()[0]
    if "--small" in sys.argv:
        window.resize(1050, 680)
    QTest.qWait(200)
    return window


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run()
        finally:
            delete(app)
