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


def verify_bundle(path):
    with ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        summary = json.loads(archive.read("summary.json"))
    counts, durations = summary["event_counts"], summary["durations"]
    assert any("Activity.qml" in key for key in durations)
    assert any("model/modelChanged" in key for key in counts)
    assert "input/dispatch" in durations and "ui/Controller.notify" in durations
    assert any(key.startswith("native/") for key in durations)
    assert manifest["complete"], manifest
    return dict(path=str(path), summary=summary, manifest=manifest)


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
    return dict(snapping=snapping, activity_open=opened, canceled=canceled, **verify_bundle(path))


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
        point = fixture(controller, window, 0.5)
        results = capture_trials(controller, window, point)
        focus_recording(controller, window)
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
