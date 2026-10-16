"""Measure navigation and native picking on a supplied anatomical mesh and 31 copies."""

import json
import sys
from pathlib import Path
from time import perf_counter as monotonic

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime


def settle(controller):
    deadline = monotonic() + 60
    while controller.session.scheduler.blocked or controller.render_model.pending:
        assert monotonic() < deadline, "Timed out"
        QTest.qWait(10)
    QTest.qWait(50)


def prepare(controller, source):
    controller.capture_mode = True
    controller.importMesh(source, 0.001, "", False)
    settle(controller)
    root = controller.session.document.entities[0].id
    leaf = controller.run("scp.duplicate", {"entity": root, "parent": root})
    settle(controller)
    for _ in range(30):
        controller.run("scp.duplicate", {"entity": leaf, "parent": root})
        settle(controller)
    controller.select(root)
    controller.frameSelection()
    QTest.qWait(500)
    return controller.rows[0]["chunks"]


def navigate(controller, window):
    center = QPoint(window.width() // 2, window.height() // 2)
    QTest.mousePress(window, Qt.MouseButton.RightButton, pos=center)
    started = monotonic()
    for step in range(90):
        QTest.mouseMove(window, center + QPoint(step * 2, step % 20), 16)
        QTest.qWait(16)
    QTest.mouseRelease(window, Qt.MouseButton.RightButton, pos=center + QPoint(180, 10))
    return monotonic() - started


def result(controller, window, source, warnings, elapsed):
    mesh = next(iter(controller.session.assets.values())).mesh
    report = dict(
        source=source,
        instances=len(controller.rows),
        triangles=mesh.counts[3],
        navigation_seconds=elapsed,
        metrics=controller.session.scheduler.metrics.report(),
        warnings=warnings,
    )
    target = Path("build/viewport-benchmark.json")
    target.write_text(json.dumps(report, indent=2))
    assert window.grabWindow().save("build/viewport-benchmark.png")
    assert not warnings, warnings
    print(json.dumps(report))


def run(source):
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        prepare(controller, source)
        controller.session.scheduler.metrics.samples.clear()
        elapsed = navigate(controller, engine.rootObjects()[0])
        result(controller, engine.rootObjects()[0], source, warnings, elapsed)
    finally:
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(sys.argv[1])
