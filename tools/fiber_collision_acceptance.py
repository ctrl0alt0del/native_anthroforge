"""Offscreen Issues navigation and a shareable native collision profile; no desktop input."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

import json
from pathlib import Path
from zipfile import ZipFile

from fiber_editor_acceptance import settle
from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from ui_acceptance import find

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/020-fiber-collisions").resolve()


def scene(controller):
    session = controller.session
    target = session.command("import", path="examples/primitives/cube.obj", units=1.0)["entity_id"]
    source = session.command(
        "curve.create", engine="POLYLINE", points=[dict(position=[x, 0, 0]) for x in (-1, 1)]
    )
    settle(controller)
    session.command(
        "fiber.create",
        curve=source,
        bindings=[dict(point=p.id, target=target) for p in session.document.object(source).points],
    )
    settle(controller)


def click(window, name):
    button = find(window, name)
    assert button.property("enabled")
    assert QMetaObject.invokeMethod(button, "clicked", Qt.DirectConnection)
    QGuiApplication.processEvents()


def inspect(controller, window):
    window.setProperty("issuesOpen", True)
    controller.issue_panel.filter("FIBER_COLLISION", "", False)
    settle(controller)
    rows = controller.issue_panel.model.rows
    assert len(rows) == 1 and rows[0]["targetLabel"] != "Removed target"
    controller.issue_panel.selectIssue(rows[0]["issueId"])
    click(window, "issueSelectTarget")
    fiber = controller.selection
    assert controller.selectedData["kind"] == "FIBER"
    click(window, "issueFrameTarget")
    controller.run("object.rename", dict(target=fiber, name="Renamed collision fiber"))
    settle(controller)
    assert controller.issue_panel.model.rows[0]["targetLabel"] == "Renamed collision fiber"


def recording(controller):
    session = controller.session
    session.command("profile.start")
    session.command("issues.recheck", provider="fiber_collisions.v1")
    settle(controller)
    path = OUTPUT / "collisions.afprofile.zip"
    session.command("profile.stop", path=str(path), wait=True)
    with ZipFile(path) as archive:
        events = json.loads(archive.read("trace.json"))["traceEvents"]
    native = [event for event in events if event["name"] == "af_path_collisions"]
    assert native and all(event["cat"] == "native" for event in native)
    print(json.dumps(dict(report=str(path), collision_calls=len(native))), flush=True)


def run():
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        scene(controller)
        inspect(controller, engine.rootObjects()[0])
        recording(controller)
        assert not warnings, warnings
        print(
            "Offscreen collision Issues selection, framing, rename and native attribution passed."
        )
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
