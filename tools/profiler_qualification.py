"""Serial, reproducible cube/body drags for dormant Qt collector qualification."""

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from snap_drag_diagnostic import DragTrial, fixture
from snap_drag_probes import Probes

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.qt_profiler import QtProfiler
from anthroforge.desktop.runtime import native_runtime


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("none", "dormant", "record"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--events", type=int, default=120)
    return parser.parse_args()


def trial_options(args):
    return SimpleNamespace(events=args.events, interval=16, probes=Probes(), spans=False)


def run_trials(controller, window, point, args, profiler):
    events, trials = [], []
    timer = QTimer()
    if args.mode == "record":
        profiler.start()
        timer.timeout.connect(lambda: events.extend(profiler.drain()))
        timer.start(100)
    for snapping in (False, True):
        trial = DragTrial(controller, window, point, snapping, trial_options(args))
        result = trial.record()
        trials.append(
            {k: v for k, v in result.items() if k not in ("inputs", "job_records", "frames")}
        )
        trial.finish()
    finish_capture(args, profiler, timer, events, trials)


def finish_capture(args, profiler, timer, events, trials):
    if args.mode == "record":
        profiler.stop()
        QTest.qWait(300)
        events.extend(profiler.drain())
    timer.stop()
    state = profiler.status() if profiler else {}
    report = dict(mode=args.mode, trials=trials, collector=state, events=events)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report), encoding="utf-8")
    print(json.dumps(dict(mode=args.mode, trials=trials, collector=state)), flush=True)


def run(args):
    profiler = QtProfiler() if args.mode != "none" else None
    controller, warnings = open_controller(None), []
    controller.capture_mode, controller.qt_profiler = True, profiler
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        point = fixture(controller, window, 0.5)
        run_trials(controller, window, point, args, profiler)
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)
        if profiler:
            profiler.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(arguments())
