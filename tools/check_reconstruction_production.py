"""Hidden multi-angle stage views on the production assembly; no anatomy mutation."""

import json
import os
import sys
from pathlib import Path

import check_reconstruction_042 as gui
from PySide6.QtCore import QSizeF, QUrl
from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtQml import QQmlComponent
from PySide6.QtQuickControls2 import QQuickStyle
from reconstruction_qualification import SCM

from anthroforge.desktop import offscreen, runtime
from anthroforge.desktop.controller import Controller

OUTPUT = Path("build/reconstruction-042/production-views")


def reference(session, source, stage):
    row = session.command(
        "reconstruction.stage.import_project",
        subject=SCM,
        stage=stage,
        path=str(source),
        source_entity=SCM,
    )
    session.wait(600)
    assert session.scheduler.registry.by_id[row["job_id"]].state == "succeeded"
    return dict(stage=row["id"])


def prepare(controller, source, original):
    session = controller.session
    session.command("open", path=str(source))
    session.wait(600)
    initial = reference(session, original, "ORIGINAL")
    transferred = reference(session, source, "TRANSFERRED")
    controller.refresh()
    controller.select(SCM)
    return [
        ("reference-base", initial, dict(stage="base")),
        ("transfer-final", transferred, dict(stage="final")),
        ("rest-final", dict(stage="rest"), dict(stage="final")),
        ("fibers", dict(stage="fibers"), dict(stage="base")),
    ]


def select_views(controller, before, after):
    panel = controller.reconstruction_compare
    panel.inspect(SCM)
    panel.selections = [
        next(r for r in panel.options if r["stage"] == value["stage"] and not r["variant"])
        for value in (before, after)
    ]
    panel.submit()
    state = controller.session.command("reconstruction.compare.status", wait=True)
    assert state["state"] == "ready", state
    panel.synchronize()
    panel.scene.focus("")
    return panel, state


def compare(app, controller, renderer, item, selection):
    name, before, after = selection
    panel, state = select_views(controller, before, after)
    (OUTPUT / (name + ".json")).write_text(json.dumps(state, indent=2))
    for label, pitch, yaw in (("front", 0, 0), ("oblique", -15, 35), ("side", 0, 90)):
        panel.scene.camera[3:5] = [pitch, yaw]
        panel.scene.changed.emit()
        capture(app, controller, renderer, name + "-" + label)


def capture(app, controller, renderer, name):
    for _ in range(20):
        app.processEvents()
        controller.process_tick()
        image = renderer.frame()
        controller.frame_presented()
    assert image.save(str(OUTPUT / (name + ".png")))


def views(app, controller, renderer, selections):
    gui.OUTPUT = OUTPUT
    path = gui.review_wrapper("ReconstructionCompareDialog")
    definition = QQmlComponent(renderer.engine)
    definition.setData(path.read_bytes(), QUrl.fromLocalFile(str(path)))
    item = definition.create()
    assert item, [e.toString() for e in definition.errors()]
    item.setParentItem(renderer.window.contentItem())
    item.setSize(QSizeF(1280, 960))
    for selection in selections:
        compare(app, controller, renderer, item, selection)
    gui.release(item)


def run(app, source, original):
    controller, warnings = Controller(), []
    controller.timer.stop()
    renderer = offscreen.Offscreen(controller, warnings)
    renderer.root.setVisible(False)
    renderer.window.setColor(QColor("#2b2c30"))
    try:
        selections = prepare(controller, source, original)
        views(app, controller, renderer, selections)
        assert not warnings and not renderer.window.isVisible(), warnings
        (OUTPUT / "result.json").write_text(json.dumps(dict(warnings=warnings, visible=False)))
    finally:
        renderer.close()
        controller.close()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(OUTPUT / "preferences.json")
    build = Path(os.environ["AF_NATIVE_BUILD"]).resolve()
    runtime.build_directory = offscreen.build_directory = lambda: build
    app = QGuiApplication([])
    QQuickStyle.setStyle("Basic")
    with runtime.native_runtime():
        run(app, Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == "__main__":
    main()
