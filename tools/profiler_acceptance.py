"""Actual F12 recording during normal/snapped curve drags, with hidden/visible Activity."""

import json
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

import numpy as np
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QGuiApplication, QKeyEvent
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from snap_drag_diagnostic import DragTrial, fixture
from snap_drag_probes import Probes
from ui_acceptance import find
from view_gesture_acceptance import position

from anthroforge.desktop import project_actions
from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime
from anthroforge.profiling import report

OUTPUT = Path("build/profiler-acceptance").resolve()


class RecordingTrial(DragTrial):
    def step(self):
        if self.index in (10, self.count - 10):
            self.toggle_recording()
        super().step()

    def toggle_recording(self):
        before = self.controller.session.history.before
        modifiers = Qt.ControlModifier if self.snapping else Qt.NoModifier
        for kind in (QEvent.KeyPress, QEvent.KeyRelease):
            QGuiApplication.sendEvent(self.window, QKeyEvent(kind, Qt.Key_F12, modifiers))
        assert find(self.window, "curveEditor").property("dragging")
        assert self.controller.session.history.before is before
        assert self.controller.session.profiler.active == (self.index == 10)


class CanceledTrial(RecordingTrial):
    def finish(self):
        QTest.keyClick(self.window, Qt.Key_Escape)
        QTest.keyRelease(self.window, Qt.Key_Control)
        QTest.mouseRelease(self.window, Qt.LeftButton, pos=self.last)
        assert self.controller.session.history.before is None
        np.testing.assert_allclose(position(self.controller, self.point_id), self.before, atol=1e-8)
        self.window.frameSwapped.disconnect(self.frame)
        self.deleteLater()


def verify_bundle(path, opened=None):
    with ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        summary = json.loads(archive.read("summary.json"))
        trace = json.loads(archive.read("trace.json"))["traceEvents"]
    durations = summary["durations"]
    assert any(key.startswith("qml.binding/") for key in durations)
    if opened is not None:
        verify_activity(trace, durations, opened)
    assert "input/dispatch" in durations and "ui/Controller.notify" in durations
    assert any(key.startswith("native/") for key in durations)
    assert manifest["complete"], manifest
    verify_interval(manifest, summary)
    return dict(path=str(path), summary=summary, manifest=manifest)


def verify_activity(trace, durations, opened):
    events = [event for event in trace if event.get("cat") == "model"]
    incremental = [event for event in events if event["args"].get("class") == "ActivityModel"]
    assert any(event["name"] == "dataChanged" for event in incremental)
    assert any(event["name"] == "rowsInserted" for event in incremental)
    assert not any(event["name"] == "modelReset" for event in incremental)
    assert not any(event["args"].get("source") == "Activity.qml" for event in events)
    if opened:
        assert any("Activity.qml" in key for key in durations)


def verify_interval(manifest, summary):
    start, stop = (v / 1000 for v in manifest["requested_interval_ns"])
    assert (
        start - 1
        <= summary["retained_interval_us"][0]
        <= summary["retained_interval_us"][1]
        <= stop + 1
    )


def trial(controller, window, point, snapping, opened, canceled=False):
    window.setProperty("activityOpen", opened)
    QTest.qWait(250)
    args = SimpleNamespace(events=100, interval=16, probes=Probes(), spans=False)
    kind = CanceledTrial if canceled else RecordingTrial
    gesture = kind(controller, window, point, snapping, args)
    result = gesture.record()
    assert result["snap_hits"] == (100 if snapping else 0)
    gesture.finish()
    await_export(controller)
    path = controller.session.profiler.path
    assert window.grabWindow().save(str(OUTPUT / f"{snapping}-{opened}.png"))
    result = verify_bundle(path, opened)
    return dict(snapping=snapping, activity_open=opened, canceled=canceled, **result)


def await_export(controller):
    for _ in range(400):
        if controller.session.profiler.done.is_set():
            break
        QTest.qWait(25)
    assert controller.session.profiler.state == "saved", controller.session.profiler.status()


def run():
    profiler, controller, warnings = QtProfiler(), open_controller(None), []
    controller.capture_mode, controller.qt_profiler = True, profiler
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        results = capture_trials(controller, window, fixture(controller, window, 0.5))
        focus_recording(controller, window)
        document_recording(controller, window)
        assert not warnings, warnings
        save_results(results)
    finally:
        controller.close()
        delete(engine)
        profiler.close()


def capture_trials(controller, window, point):
    results = [
        trial(controller, window, point, snap, opened)
        for opened in (False, True)
        for snap in (False, True)
    ]
    results.append(trial(controller, window, point, True, False, True))
    return results


def focus_recording(controller, window):
    field = find(window, "outlinerSearch")
    field.forceActiveFocus()
    focus = window.activeFocusItem()
    QTest.keyClick(window, Qt.Key_F12)
    assert controller.session.profiler.active and window.activeFocusItem() is focus
    event = QKeyEvent(QEvent.KeyPress, Qt.Key_X, Qt.NoModifier, "PRIVATE_TEXT_SENTINEL")
    QGuiApplication.sendEvent(window, event)
    QTest.keyClick(window, Qt.Key_F12)
    assert not controller.session.profiler.active and window.activeFocusItem() is focus
    await_export(controller)
    with ZipFile(controller.session.profiler.path) as archive:
        assert b"PRIVATE_TEXT_SENTINEL" not in archive.read("trace.json")
    field.setProperty("text", "")


def document_recording(controller, window):
    profiler = controller.profiler
    path = str(OUTPUT / "document-lifecycle.anthroforge")
    controller.session.command("save", path=path, blocked_policy="wait")
    replace_document(controller, "")
    QTest.keyClick(window, Qt.Key_F12)
    for target in (path, "", path):
        replace_document(controller, target)
        assert controller.profiler is profiler and profiler.active
        assert controller.session.scheduler.profiler is profiler
    QTest.keyClick(window, Qt.Key_F12)
    await_export(controller)
    verify_bundle(profiler.path)


def replace_document(controller, path):
    controller.replaceDocument(path)
    for _ in range(400):
        project_actions.poll(controller)
        controller.session.scheduler.tick()
        QTest.qWait(25)
        if controller.pending_document is None and not controller.session.waiting_save:
            return
    raise AssertionError("Document replacement did not finish")


def save_results(results):
    (OUTPUT / "acceptance.json").write_text(json.dumps(results, indent=2))
    print(
        json.dumps(
            [
                dict(path=r["path"], snapping=r["snapping"], activity=r["activity_open"])
                for r in results
            ]
        ),
        flush=True,
    )


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report.default_directory = lambda: OUTPUT
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run()
        finally:
            delete(app)
