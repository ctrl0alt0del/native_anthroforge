"""Background native renderer acceptance for historical shortcut geometry."""

import json
from dataclasses import asdict
from pathlib import Path
from zipfile import ZipFile

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from shortcut_inspection_acceptance import anchor_fixture
from shortcuts_scene_acceptance import frames

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.feedback_editor import FeedbackEditor
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime
from anthroforge.feedback.storage import LocalReportConsumer

OUTPUT = Path("build/shortcut-comparison-review")


def capture(controller, renderer, application, name):
    image = frames(controller, renderer, application)
    assert image.save(str(OUTPUT / (name + ".png")))
    return image


def exercise(controller, renderer, application):
    key = anchor_fixture(controller)
    tool = controller.shortcut_comparison
    tool.capture(key)
    baseline = capture(controller, renderer, application, "baseline")
    edit(controller, key, 2)
    controller.session.wait(10)
    after = capture(controller, renderer, application, "after")
    assert baseline != after
    export_report(controller)
    feedback_report(controller, after, application)
    modes(controller, renderer, application, key)


def export_report(controller):
    path = (OUTPUT / "comparison.afinspection.zip").resolve()
    controller.session.command("inspection.export", path=str(path), replay=True, wait=True)
    result = controller.session.command("inspection.replay", path=str(path))
    assert result["comparison"]["changed"] >= 1


def feedback_report(controller, image, application):
    editor = FeedbackEditor(controller, LocalReportConsumer(OUTPUT / "inbox"))
    try:
        editor.begin_draft(image)
        revision = controller.session.document.revision
        assert editor.comparison and not editor.include_replay
        editor.submit("bug", "Frozen shortcut comparison acceptance")
        while editor.service.future is not None:
            application.processEvents()
            editor.poll()
        assert editor.service.state == "saved", editor.service.error
        inspect_feedback(editor.service.location, revision)
    finally:
        editor.close()


def inspect_feedback(path, revision):
    from io import BytesIO

    with ZipFile(path) as archive:
        payload = archive.read("comparison.afinspection.zip")
    with ZipFile(BytesIO(payload)) as archive:
        assert "starting.anthroforge" not in archive.namelist()
        assert json.loads(archive.read("inspection.json"))["revision"] == revision


def modes(controller, renderer, application, key):
    tool = controller.shortcut_comparison
    tool.setMode("Before")
    capture(controller, renderer, application, "before")
    assert tool.before and tool.model.active_rows()
    edit(controller, key, 1.8)
    assert not tool.before
    controller.session.wait(10)
    tool.setMode("Overlay")
    capture(controller, renderer, application, "overlay")
    assert tool.model.leases
    tool.clear()
    capture(controller, renderer, application, "cleared")
    assert not tool.model.leases


def edit(controller, key, value):
    ref = next(s.reference for s in controller.session.document.shortcuts if s.id == key)
    controller.run("shortcut.set", dict(reference=asdict(ref), value=value))
    assert controller.session.document.entity(ref.target).matrix[0] == value


def run(application):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, application)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    application = QGuiApplication([])
    with native_runtime():
        run(application)
