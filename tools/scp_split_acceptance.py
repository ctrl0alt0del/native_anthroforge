"""Background-only desktop validation of connected SCP splitting and native presentation."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
if os.name == "nt":
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ["SystemRoot"], "Fonts"))

from pathlib import Path

from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import find

from anthroforge.application import primitive_operations
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/parity-workflows-034/split")


def settle(controller):
    controller.session.wait(10)
    controller.refresh()
    for _ in range(100):
        QTest.qWait(20)
        if not controller.render_model.pending:
            break
    QTest.qWait(150)


def setup(controller):
    root = controller.run("scp.empty", dict(name="Root"))
    target = controller.run("primitive.create", dict(kind="BODY", shape="BOX", parent=root))
    settle(controller)
    curve = primitive_operations.definition(controller.session, target).curves[0]
    controller.run(
        "point.insert",
        dict(entity=target, curve=curve.id, index=1, point=dict(position=[0, 0.25, 0.15])),
    )
    settle(controller)
    controller.selection_view.select(target)
    controller.authoring.setEditing(True)
    controller.viewport_view.frameSelection()
    return target


def exercise(controller, engine, target):
    editor = controller.authoring
    rows = [r for r in editor.componentRows if r.get("part") == "position"]
    editor.selectComponent(rows[1]["key"], False)
    settle(controller)
    window = engine.rootObjects()[0]
    assert window.grabWindow().save(str(OUTPUT / "before.png"))
    button = find(window, "splitSCP")
    assert button.property("enabled")
    assert QMetaObject.invokeMethod(button, "clicked", Qt.DirectConnection)
    settle(controller)
    assert controller.selection_view.selectedData["kind"] == "HOOK"
    assert len(controller.session.document.entities) == 3
    assert controller.session.document.entity(target).primitive
    assert window.grabWindow().save(str(OUTPUT / "after.png"))


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = Controller(), []
    controller.capture_mode = True
    engine = create_engine(controller, warnings)
    try:
        target = setup(controller)
        exercise(controller, engine, target)
        assert not controller.message, controller.message
        assert not warnings, warnings
        print("Offscreen SCP split: button, shared Hook and first identity passed.")
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
