"""Rendered camera navigation during production-resolution native field work."""

import json
from dataclasses import replace
from functools import partial
from pathlib import Path
from time import perf_counter, process_time

import numpy as np
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from anthroforge.core.jobs import Job
from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.runtime import native_runtime
from anthroforge.native.skin_fields import prepare

OUTPUT = Path("build/viewport-worker-review").resolve()


def source():
    vertices = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
    faces = np.array([[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]])
    return vertices, faces, np.ones(4, dtype=np.uint8), np.ones(4)


def compute(engine, cancel):
    for _ in range(3):
        fields = prepare(engine, *source(), resolution=220, cancel=cancel.handle)
        fields.close()


def start_work(controller):
    session, jobs = controller.session, []
    for index in range(4):
        job = field_job(session, index)
        session.scheduler.submit(job)
        jobs.append(job)
    return jobs


def field_job(session, index):
    from anthroforge.native.mesh import NativeCancellation

    return Job(
        f"Acceptance field {index}",
        frozenset(),
        lambda _: session.engine,
        compute,
        lambda _: None,
        kind="skin_envelope",
        writes=False,
        cancel=NativeCancellation(session.engine),
    )


def fixture(controller):
    session = controller.session
    root = session.command("scp.empty", name="Responsiveness fixture")
    path = str(Path("examples/primitives/cube.obj").resolve())
    identity = session.command("import", path=path, units=1.0, parent=root)["entity_id"]
    session.command("wait")
    original = session.document.entity(identity)
    cubes = tuple(replace(original, id=f"probe-{i}", name=f"Cube {i}") for i in range(64))
    session.replace_document(entities=(session.document.entity(root), *cubes))
    session.command("mirror.configure", target=root, enabled=True, shift=2)
    session.command("wait")
    controller.refresh()


def statistics(values):
    ordered = sorted(values)
    assert ordered, "The viewport did not present frames."
    return dict(count=len(values), p95_ms=ordered[int(len(ordered) * 0.95)], max_ms=max(values))


def move_camera(controller, samples):
    step = len(samples)
    values = [1 + 0.05 * np.sin(step / 12), 0, 0, -20, 25 + step * 0.3, 0, 6 + step % 10 * 0.01]
    started = perf_counter()
    controller.cameraRequested.emit(values, False)
    controller.viewport_view.saveCamera(values, False)
    samples.append((perf_counter() - started) * 1000)


def navigate(controller, calls):
    loop, camera, heartbeat = QEventLoop(), QTimer(), QTimer()
    beats = []
    camera.timeout.connect(lambda: move_camera(controller, calls))
    heartbeat.timeout.connect(lambda: beats.append(perf_counter()))
    camera.start(16)
    heartbeat.start(10)
    QTimer.singleShot(4500, loop.quit)
    loop.exec()
    return statistics(np.diff(beats) * 1000)


def record_frame(frames):
    frames.append(perf_counter())


def condition(controller, window, work):
    calls, frames = [], []
    observed = partial(record_frame, frames)
    window.frameSwapped.connect(observed)
    before = {job.id for job in controller.session.scheduler.jobs}
    jobs = start_work(controller) if work else []
    result = measured_navigation(controller, frames, calls)
    window.frameSwapped.disconnect(observed)
    verify_jobs(controller, before, jobs)
    return dict(work=work, **result)


def measured_navigation(controller, frames, calls):
    cpu, wall = process_time(), perf_counter()
    beats = navigate(controller, calls)
    return dict(
        heartbeat=beats,
        camera=statistics(calls),
        cpu_seconds=process_time() - cpu,
        wall_seconds=perf_counter() - wall,
        frames=statistics(np.diff(frames) * 1000),
    )


def verify_jobs(controller, before, jobs):
    controller.session.command("wait")
    actual = {job.id for job in controller.session.scheduler.jobs} - before
    assert actual == {job.id for job in jobs}, "Camera navigation scheduled domain work."
    assert all(job.state == "succeeded" for job in jobs)
    assert not controller.session.scheduler.errors


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = open_controller(None), []
    fixture(controller)
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        QTest.qWait(500)
        rows = [condition(controller, window, work) for work in (False, True)]
        assert window.grabWindow().save(str(OUTPUT / "navigation.png"))
        assert not warnings, warnings
        (OUTPUT / "acceptance.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(json.dumps(rows))
    finally:
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
