"""Exercise actual skin buttons and hidden GPU publication for both remeshers."""

import json
import os
import sys
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import click

from anthroforge.application import skin_evaluation
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime


def setup(controller, window):
    skin_evaluation.TARGET_RESOLUTION = 220
    bone = controller.run(
        "import", dict(path=str(Path("examples/primitives/cube.obj").resolve()), units=1)
    )
    controller.session.wait()
    controller.selection_view.select(bone["entity_id"])
    controller.run("workspace.update", dict(hidden=[bone["entity_id"]]))
    controller.cameraRequested.emit([0, 0, 0, -18, 25, 0, 3], False)
    controller.run(
        "skin.configure", dict(section="topology_settings", values=dict(target_quads=8100))
    )
    controller.refresh()
    QTest.qWait(150)
    click(window, "skinTab")


def capture(controller, window, output, backend):
    for stage in ("ENVELOPE", "TOPOLOGY"):
        controller.run("workspace.update", dict(skin_display=stage))
        controller.refresh()
        QTest.qWait(100)
        assert window.grabWindow().save(str(output / f"{backend}-{stage}-controls.png"))
    state = controller.session.document.skin.topology
    rows = controller.render_model.rows
    assert any(row["geometry_asset"] == state.asset for row in rows)
    payload = controller.session.resources.skin[state.data]
    return json.loads(payload.metadata)


def build(controller, window, output, backend):
    controller.run(
        "skin.configure", dict(section="topology_settings", values=dict(backend=backend))
    )
    controller.refresh()
    controller.session.command("profile.start")
    click(window, "skinBuild")
    controller.session.wait()
    controller.refresh()
    QTest.qWait(200)
    assert not controller.session.scheduler.errors, controller.session.scheduler.errors
    assert window.grabWindow().save(str(output / f"{backend}-controls.png"))
    controller.session.command(
        "profile.stop", path=str(output / f"{backend}.afprofile.zip"), wait=True
    )


def exercise(app, output):
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        setup(controller, window)
        reports = run_cases(controller, window, output)
        (output / "acceptance.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)
        app.processEvents()


def run_cases(controller, window, output):
    reports = {}
    for backend in ("INSTANT", "QUADWILD"):
        build(controller, window, output, backend)
        reports[backend] = capture(controller, window, output, backend)
        controller.session.command(
            "save", path=str(output / f"{backend}.anthroforge"), blocked_policy="wait"
        )
        controller.session.wait()
    return reports


def main():
    output = Path(sys.argv[1]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(output / "preferences.json")
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        exercise(app, output)
    print("Skin topology buttons and profiles verified offscreen; GPU review is separate.")


if __name__ == "__main__":
    main()
