"""Offscreen direct engine selection and adaptive sampling on the supplied project."""

import json
import os
import sys
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
if sys.platform == "win32":
    os.environ.setdefault("QT_QPA_FONTDIR", str(Path(os.environ["SystemRoot"]) / "Fonts"))

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import Q_ARG, QMetaObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from snapped_routing_acceptance import capture, choose, selector, settle

from anthroforge.application import projects, storage
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime
from tests.test_routing_layout_workflow import accepted


def load(controller, source):
    session = controller.session
    projects.adopt(session, *storage.read_package(source, session.engine))
    key = session.document.objects[0].id
    before = session.document.object(key)
    session.command("curve.evaluate", curve=key)
    settle(controller)
    assert session.document.object(key).points == before.points
    path = accepted(session, key)
    assert path.count == 24 and session.document.object(key).engine_settings.samples == 24
    controller.select(key)
    settle(controller)
    return key, before.points


def conversion(controller, window, key):
    choose(window, 0)
    settle(controller)
    cursor = controller.session.history.cursor
    choose(window, 2)
    settle(controller)
    assert controller.session.history.cursor == cursor + 1
    accepted(controller.session, key)
    controller.run("undo", {})
    settle(controller)
    assert controller.session.document.object(key).engine == "BEZIER"
    controller.run("redo", {})
    settle(controller)
    accepted(controller.session, key)


def sampling_control(controller, window, key):
    controller.select(key)
    controller.authoring.setEditing(True)
    settle(controller)
    advanced = selector(window, "routingAdvanced")
    advanced.setProperty("checked", True)
    settle(controller)
    return selector(window, "routingSamples")


def growth(controller, window, key):
    setting = sampling_control(controller, window, key)
    assert setting.property("label") == "Preferred samples"
    assert QMetaObject.invokeMethod(setting, "edited", Qt.DirectConnection, Q_ARG(float, 4))
    settle(controller)
    path = accepted(controller.session, key)
    assert path.count > 4 and controller.session.document.object(key).engine_settings.samples == 4
    controller.run("curve.evaluate", dict(curve=key))
    settle(controller)
    accepted(controller.session, key)
    return path.count


def exercise(controller, window, source, output):
    key, points = load(controller, source)
    conversion(controller, window, key)
    count = growth(controller, window, key)
    assert controller.session.document.object(key).points == points
    capture(window, output / "routing-controls.png")
    controller.run("undo", {})
    settle(controller)
    save_original_settings(controller, key, output)
    return summary(count)


def save_original_settings(controller, key, output):
    controller.run("curve.engine_settings", dict(curve=key, samples=24, accepted_steps=64))
    settle(controller)
    accepted(controller.session, key)
    controller.session.command(
        "save", path=str(output / "corrected.anthroforge"), blocked_policy="wait"
    )


def summary(count):
    return dict(
        original_samples=24,
        preferred_samples=4,
        grown_samples=count,
        direct_selection=True,
        undo_redo=True,
        unchanged_points=True,
        clear_segments=True,
    )


def run(source, output):
    output.mkdir(parents=True, exist_ok=True)
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        result = exercise(controller, engine.rootObjects()[0], source, output)
        assert not warnings, warnings
        (output / "gui-acceptance.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result))
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
