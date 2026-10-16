"""Exercise parent/child motion with actual viewport drags and frame observations."""

import json
import sys
from pathlib import Path

from gui_acceptance import health
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from anthroforge.desktop.app import create_engine, open_controller, prepare_view
from anthroforge.desktop.runtime import native_runtime


def observe(controller, ids, baseline, samples):
    rows = {row["id"]: row for row in controller.render_model.rows}
    if not all(key in rows for key in ids):
        return
    offsets = [rows[key]["matrix"][3] - baseline[key] for key in ids]
    samples.append({"parent": offsets[0], "child": offsets[1]})


def drag_frames(window, output):
    point = QPoint(*map(round, health(window)["gizmo"]))
    QTest.mousePress(window, Qt.MouseButton.LeftButton, pos=point)
    for step in range(1, 21):
        QTest.mouseMove(window, point + QPoint(step * 5, 0), 16)
        QTest.qWait(18)
        if step in (5, 15):
            assert window.grabWindow().save(str(output / f"drag-{step}.png"))
    QTest.mouseRelease(window, Qt.MouseButton.LeftButton, pos=point + QPoint(100, 0))
    QTest.qWait(100)


def inspect(controller, window, output):
    ids = [entity.id for entity in controller.session.document.entities[:2]]
    baseline = {row["id"]: row["matrix"][3] for row in controller.render_model.rows}
    samples, first = [], len(controller.session.scheduler.jobs)
    window.frameSwapped.connect(lambda: observe(controller, ids, baseline, samples))
    drag_frames(window, output)
    jobs = controller.session.scheduler.jobs[first:]
    report = summarize(jobs, samples, controller)
    (output / "report.json").write_text(json.dumps(report, indent=2))
    assert samples and max(abs(s["parent"]) for s in samples) > 0.05
    assert report["max_parent_child_error"] < 1e-6, report
    assert all(job.state == "succeeded" and job.execution == "inline" for job in jobs), report
    assert not controller.session.scheduler.errors
    print(json.dumps(report))


def summarize(jobs, samples, controller):
    return {
        "frames": len(samples),
        "updates": len(jobs),
        "inline_updates": sum(j.execution == "inline" for j in jobs),
        "max_parent_child_error": max(abs(s["parent"] - s["child"]) for s in samples),
        "max_update_ms": max(j.prepare_ms + j.compute_ms + j.publish_ms for j in jobs),
        "metrics": controller.session.scheduler.metrics.report(),
    }


def run(project, output):
    output.mkdir(parents=True, exist_ok=True)
    controller, warnings = open_controller(project), []
    controller.capture_mode = True
    engine = create_engine(controller, warnings)
    prepare_view(controller, project)
    try:
        QTest.qWait(1000)
        inspect(controller, engine.rootObjects()[0], output)
        assert not warnings, warnings
    finally:
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(sys.argv[1], Path("build/scheduling-acceptance").resolve())
