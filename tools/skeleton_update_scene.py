"""Actual synchronized review views on a hidden GPU texture, never desktop automation."""

import cProfile
import json
import os
import sys
from pathlib import Path
from time import perf_counter, sleep

from PySide6.QtCore import QSize, QSizeF, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlComponent

from anthroforge.desktop import offscreen, runtime, style
from anthroforge.desktop.controller import Controller

OUTPUT = Path("build/skeleton-update-042/gui")
QML = Path("src/anthroforge/desktop/qml").resolve()
ANGLES = (("front", 0, 0), ("side", 0, 90), ("back", 0, 180), ("oblique", -15, 35))
TIMINGS = []


class ReviewRenderer(offscreen.Offscreen):
    def load_view(self):
        self.engine.addImportPath(str(QML))
        self.component = QQmlComponent(self.engine, QUrl.fromLocalFile(str(wrapper())))
        while self.component.isLoading():
            QGuiApplication.processEvents()
        self.root = self.component.create()
        assert self.root is not None, [e.toString() for e in self.component.errors()]
        self.size = QSize(1440, 1000)
        self.root.setSize(QSizeF(self.size))
        self.window.contentItem().setSize(QSizeF(self.size))
        self.window.setGeometry(0, 0, self.size.width(), self.size.height())
        self.root.setParentItem(self.window.contentItem())


def wrapper():
    path = (OUTPUT / "Review.qml").resolve()
    text = 'import QtQuick\nimport "' + QML.as_uri() + '"\n'
    text += "Item { SkeletonUpdateDialog { Component.onCompleted: open() } }"
    path.write_text(text, "utf-8")
    return path


def wait(app, controller, renderer):
    elapsed, deadline = [], perf_counter() + 600
    while perf_counter() < deadline:
        started = perf_counter()
        frame(app, controller, renderer)
        require_progress(controller.skeleton_panel)
        elapsed.append(perf_counter() - started)
        if controller.skeleton_panel.state.get("ready") and not any(
            m.pending for m in controller.skeleton_panel.scene.models
        ):
            return elapsed
        sleep(0.005)
    raise TimeoutError(str(controller.skeleton_panel.state))


def frame(app, controller, renderer):
    for action in (
        app.processEvents,
        controller.process_tick,
        renderer.frame,
        controller.frame_presented,
    ):
        started = perf_counter()
        cpu = cProfile.Profile()
        cpu.runcall(action)
        row = dict(
            phase=action.__name__,
            seconds=perf_counter() - started,
            state=controller.skeleton_panel.state.get("state"),
        )
        TIMINGS.append(row)
        if row["seconds"] > 0.3:
            print("slow phase", row, flush=True)
            cpu.dump_stats(str(OUTPUT / (action.__name__ + ".pstats")))


def require_progress(panel):
    state = panel.state
    log_progress(panel, state)
    if state.get("error") or state.get("source_error"):
        raise RuntimeError(state.get("error") or state.get("source_error"))
    if state.get("state") == "ready" and not state.get("ready"):
        raise RuntimeError(str(state.get("findings")))


def log_progress(panel, state):
    job = panel.controller.session.scheduler.registry.by_id.get(state.get("job_id"))
    stamp = (state.get("source_state"), state.get("state"), job.state if job else "")
    if stamp != getattr(panel, "qualification_stamp", None):
        panel.qualification_stamp = stamp
        print("progress", stamp, job.progress if job else "", flush=True)


def views(app, controller, renderer):
    scene = controller.skeleton_panel.scene
    scene.filter("fibers", False)
    for label, pitch, yaw in ANGLES:
        scene.camera[3:5] = [pitch, yaw]
        scene.changed.emit()
        for _ in range(5):
            app.processEvents()
            renderer.frame()
            controller.frame_presented()
        assert renderer.frame().save(str(OUTPUT / (label + ".png")))


def run(app, source, replacement):
    controller, warnings = Controller(), []
    controller.timer.stop()
    renderer = None
    try:
        controller.session.command("open", path=source)
        controller.session.wait(600)
        controller.refresh()
        renderer = ReviewRenderer(controller, warnings)
        inspect(app, controller, renderer, replacement, warnings)
    finally:
        if renderer:
            renderer.close()
        controller.close()


def inspect(app, controller, renderer, replacement, warnings):
    panel = controller.skeleton_panel
    controller.session.command("profile.start")
    panel.inspect(replacement)
    frames = ("SCP_8:driver-frame", "SCP_9:driver-frame", "SCP_12:driver-frame")
    panel.options["mappings"] = {key: dict(action="include") for key in frames}
    elapsed = wait(app, controller, renderer)
    views(app, controller, renderer)
    assert not renderer.window.isVisible() and not warnings, warnings
    evidence(panel, elapsed, warnings)
    controller.session.command("profile.stop", path=str(OUTPUT / "review.afprofile.zip"), wait=True)
    (OUTPUT / "phases.json").write_text(json.dumps(TIMINGS), "utf-8")


def evidence(panel, elapsed, warnings):
    result = dict(
        ready=panel.state["ready"],
        warnings=warnings,
        hidden=True,
        gui_iteration_s=dict(maximum=max(elapsed), p95=sorted(elapsed)[int(len(elapsed) * 0.95)]),
        shown=[len(m.displayed) for m in panel.scene.models],
    )
    (OUTPUT / "evidence.json").write_text(json.dumps(result, indent=2), "utf-8")
    print(json.dumps(result), flush=True)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(OUTPUT / "preferences.json")
    build = Path(os.environ.get("AF_NATIVE_BUILD", "build/dev")).resolve()
    runtime.build_directory = offscreen.build_directory = lambda: build
    style.configure()
    app = QGuiApplication([])
    with runtime.native_runtime():
        run(app, sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
