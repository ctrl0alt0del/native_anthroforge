"""Serial cube/body comparisons using the complete runtime recorder and real input."""

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

from activity_benchmark import ModalTrial
from profiler_system_load import system_load, system_times
from PySide6.QtCore import Qt
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from snap_drag_diagnostic import DragTrial, fixture
from snap_drag_probes import Probes

from anthroforge import __version__
from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime


class BenchmarkTrial(DragTrial):
    def finish(self):
        assert self.controller.session.history.before is not None, (
            "Benchmark gesture ended before release",
            self.window.isActive(),
        )
        super().finish()


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("none", "dormant", "record"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--events", type=int, default=120)
    parser.add_argument("--seconds", type=int, default=120)
    parser.add_argument("--warmup", type=int, default=0)
    parser.add_argument("--background", action="store_true")
    parser.add_argument("--activity-open", action="store_true")
    parser.add_argument("--interaction", choices=("drag", "modal"), default="drag")
    return parser.parse_args()


def run_trials(controller, window, point, args):
    trials, load = [], system_times()
    if args.mode == "record":
        controller.session.command("profile.start", seconds=args.seconds)
    options = SimpleNamespace(events=args.events, interval=16, probes=Probes(), spans=False)
    for snapping in (False, True):
        kind = ModalTrial if args.interaction == "modal" else BenchmarkTrial
        trial = kind(controller, window, point, snapping, options)
        trials.append(record_trial(trial))
        trial.finish()
    finish_capture(args, controller, trials, system_load(load))


def record_trial(trial):
    result = trial.record()
    assert result["snap_hits"] == (trial.count if trial.snapping else 0)
    return {k: v for k, v in result.items() if k not in ("inputs", "job_records", "frames")}


def finish_capture(args, controller, trials, load):
    if args.mode == "record":
        controller.session.command(
            "profile.stop", path=str(args.output.with_suffix(".afprofile.zip"))
        )
        for _ in range(1200):
            if controller.session.profiler.done.is_set():
                break
            QTest.qWait(25)
        assert controller.session.profiler.state == "saved", controller.session.profiler.status()
    save_result(args, controller.session.profiler.status(), trials, load)


def save_result(args, state, trials, load):
    report = dict(settings(args), trials=trials, profiler=state, system_load=load)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report), encoding="utf-8")
    print(json.dumps(dict(mode=args.mode, trials=trials, system_load=load)), flush=True)


def settings(args):
    return dict(
        mode=args.mode,
        activity_open=args.activity_open,
        interaction=args.interaction,
        background=args.background,
        version=__version__,
    )


def run(args):
    profiler = QtProfiler() if args.mode != "none" else None
    controller, warnings = open_controller(None), []
    controller.capture_mode, controller.qt_profiler = True, profiler
    engine = create_engine(controller, warnings)
    try:
        exercise(controller, engine.rootObjects()[0], args)
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)
        if profiler:
            profiler.close()


def exercise(controller, window, args):
    window.activeChanged.connect(lambda: print("Window active:", window.isActive(), flush=True))
    if args.background:
        window.setFlag(Qt.WindowDoesNotAcceptFocus, True)
        window.show()
    else:
        window.requestActivate()
    point = fixture(controller, window, 0.5)
    window.setProperty("activityOpen", args.activity_open)
    QTest.qWait(250)
    warmup(controller, window, point, args.warmup)
    run_trials(controller, window, point, args)


def warmup(controller, window, point, count):
    if count:
        args = SimpleNamespace(events=count, interval=16, probes=Probes(), spans=False)
        trial = DragTrial(controller, window, point, False, args)
        trial.record()
        trial.finish()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run(arguments())
        finally:
            delete(app)
