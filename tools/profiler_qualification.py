"""Serial cube/body comparisons using the complete runtime recorder and real input."""

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

from profiler_system_load import system_load, system_times
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from snap_drag_diagnostic import DragTrial, fixture
from snap_drag_probes import Probes

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("none", "dormant", "record"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--events", type=int, default=120)
    parser.add_argument("--seconds", type=int, default=120)
    return parser.parse_args()


def run_trials(controller, window, point, args):
    trials, load = [], system_times()
    if args.mode == "record":
        controller.session.command("profile.start", seconds=args.seconds)
    options = SimpleNamespace(events=args.events, interval=16, probes=Probes(), spans=False)
    for snapping in (False, True):
        trial = DragTrial(controller, window, point, snapping, options)
        result = trial.record()
        trials.append(
            {k: v for k, v in result.items() if k not in ("inputs", "job_records", "frames")}
        )
        trial.finish()
    finish_capture(args, controller, trials, system_load(load))


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
    state = controller.session.profiler.status()
    report = dict(mode=args.mode, trials=trials, profiler=state, system_load=load)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report), encoding="utf-8")
    print(json.dumps(dict(mode=args.mode, trials=trials, system_load=load)), flush=True)


def run(args):
    profiler = QtProfiler() if args.mode != "none" else None
    controller, warnings = open_controller(None), []
    controller.capture_mode, controller.qt_profiler = True, profiler
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        point = fixture(controller, window, 0.5)
        run_trials(controller, window, point, args)
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)
        if profiler:
            profiler.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run(arguments())
        finally:
            delete(app)
