"""Controlled normal/snapped Body drags; diagnostic recordings, not a profiler product."""

import argparse
import cProfile
import json
import math
import pstats
from pathlib import Path
from time import perf_counter, process_time, thread_time

import numpy as np
from curve_interaction_acceptance import LEFT, move, screen
from primitive_acceptance import settle
from PySide6.QtCore import QEvent, QEventLoop, QObject, QPoint, QPointF, Qt, QTimer, Slot
from PySide6.QtGui import QGuiApplication, QMouseEvent
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from ui_acceptance import find
from view_gesture_acceptance import position, select_point

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.runtime import native_runtime


def summary(values):
    return (
        dict(
            count=len(values),
            mean=float(np.mean(values)),
            p95=float(np.percentile(values, 95)),
            maximum=float(np.max(values)),
        )
        if values
        else dict(count=0)
    )


def fixture(controller, window):
    path = str(Path("examples/primitives/cube.obj").resolve())
    root = controller.run("import", dict(path=path, units=1))["entity_id"]
    settle(controller)
    body = controller.run("primitive.create", dict(kind="BODY", parent=root))
    settle(controller)
    controller.select(body)
    controller.authoring.setEditing(True)
    window.resize(1500, 950)
    controller.cameraRequested.emit([0, 0, 0, -90, 0, 0, 3], True)
    QTest.qWait(250)
    find(window, "viewport").forceActiveFocus()
    return select_point(controller, body)


def deliver_move(window, point, snapping):
    modifiers = Qt.ControlModifier if snapping else Qt.NoModifier
    event = QMouseEvent(
        QEvent.MouseMove,
        QPointF(point),
        window.mapToGlobal(QPointF(point)),
        Qt.NoButton,
        LEFT,
        modifiers,
    )
    event.setTimestamp(round(perf_counter() * 1000))
    QGuiApplication.sendEvent(window, event)


class DragTrial(QObject):
    def __init__(self, controller, window, point_id, snapping, args):
        super().__init__(window)
        self.controller, self.window, self.point_id = controller, window, point_id
        self.snapping, self.count, self.interval = snapping, args.events, args.interval
        self.frames, self.inputs, self.snap_hits, self.index = [], [], 0, 0
        self.timer, self.loop = QTimer(self), QEventLoop()
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.step)
        self.window.frameSwapped.connect(self.frame)
        self.first = screen(window, [-0.25, 0, 0.5])
        self.last = self.first

    @Slot()
    def frame(self):
        self.frames.append(perf_counter())

    def begin(self):
        self.controller.session.scheduler.metrics.samples.clear()
        pointer = move(self.window, position(self.controller, self.point_id))
        QTest.mousePress(self.window, LEFT, pos=pointer)
        QTest.mouseMove(self.window, self.first, 0)
        if self.snapping:
            QTest.keyPress(self.window, Qt.Key_Control)
        QTest.qWait(200)
        assert find(self.window, "curveEditor").property("dragging")
        self.frames.clear()
        self.jobs = len(self.controller.session.scheduler.jobs)

    @Slot()
    def step(self):
        started = perf_counter()
        angle = self.index * 2 * math.pi / 60
        self.last = self.first + QPoint(round(45 * math.sin(angle)), round(25 * math.cos(angle)))
        deliver_move(self.window, self.last, self.snapping)
        self.inputs.append(dict(at=started, duration_ms=(perf_counter() - started) * 1000))
        self.snap_hits += bool(self.controller.authoring.interaction.snap)
        self.index += 1
        if self.index >= self.count:
            self.timer.stop()
            self.loop.quit()

    def record(self, profile):
        self.begin()
        started, cpu, main_cpu = perf_counter(), process_time(), thread_time()
        if profile:
            profile.enable()
        self.timer.start(self.interval)
        self.loop.exec()
        if profile:
            profile.disable()
        return self.result(started, cpu, main_cpu)

    def result(self, started, cpu, main_cpu):
        frames = (np.diff(self.frames) * 1000).tolist()
        jobs = self.controller.session.scheduler.jobs[self.jobs :]
        result = dict(
            seconds=perf_counter() - started,
            process_cpu_s=process_time() - cpu,
            main_cpu_s=thread_time() - main_cpu,
            frame_ms=summary(frames),
            jobs=len(jobs),
            job_compute_ms=summary([j.compute_ms for j in jobs]),
        )
        return dict(result, **self.input_result())

    def input_result(self):
        return dict(
            snapping=self.snapping,
            snap_hits=self.snap_hits,
            events=self.index,
            handler_ms=summary([v["duration_ms"] for v in self.inputs]),
            frames=self.frames,
            inputs=self.inputs,
            metrics=self.controller.session.scheduler.metrics.report(),
        )

    def finish(self):
        if self.snapping:
            QTest.keyRelease(self.window, Qt.Key_Control)
        QTest.mouseRelease(self.window, LEFT, pos=self.last)
        settle(self.controller)
        self.controller.run("undo", {})
        settle(self.controller)
        self.window.frameSwapped.disconnect(self.frame)
        self.deleteLater()


def profile_report(profile):
    rows = []
    for (file, line, name), (_primitive, calls, own, total, _callers) in pstats.Stats(
        profile
    ).stats.items():
        rows.append(dict(file=file, line=line, name=name, calls=calls, self_s=own, total_s=total))
    return sorted(rows, key=lambda row: row["total_s"], reverse=True)


def save_report(args, results):
    args.output.write_text(json.dumps(dict(results=results), indent=2))
    report = {k: v for k, v in results[-1].items() if k not in ("profile", "frames", "inputs")}
    print(json.dumps(report), flush=True)


def run_trial(controller, window, point_id, snapping, args):
    trial = DragTrial(controller, window, point_id, snapping, args)
    profile = cProfile.Profile() if args.profile else None
    report = trial.record(profile)
    if profile:
        report["profile"] = profile_report(profile)
    window.grabWindow().save(str(args.output.with_suffix(".png")))
    return trial, report


def run_trials(controller, window, point_id, args):
    results = []
    modes = [False, True, True, False] if args.mode == "both" else [args.mode == "snap"]
    for snapping in modes * args.repeats:
        trial, report = run_trial(controller, window, point_id, snapping, args)
        results.append(report)
        save_report(args, results)
        trial.finish()
    return results


def run(args):
    args.output.parent.mkdir(parents=True, exist_ok=True)
    controller, warnings = open_controller(None), []
    controller.capture_mode = True
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        point_id = fixture(controller, window)
        results = run_trials(controller, window, point_id, args)
        args.output.write_text(json.dumps(dict(results=results, warnings=warnings), indent=2))
        assert not warnings, warnings
    finally:
        controller.close()


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=Path("build/snap-drag-investigation/baseline.json")
    )
    parser.add_argument("--profile", action="store_true")
    parser.add_argument("--mode", choices=("both", "normal", "snap"), default="both")
    parser.add_argument("--events", type=int, default=180)
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--interval", type=int, default=16)
    return parser.parse_args()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(arguments())
