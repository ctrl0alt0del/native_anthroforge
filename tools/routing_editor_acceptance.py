"""Offscreen routing controls, source preservation, component selection and undo."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from ui_acceptance import find

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime


def settle(controller):
    controller.session.wait(15)
    controller.refresh()
    QGuiApplication.processEvents()


def setup(controller):
    controller.run("import", dict(path="examples/primitives/cube.obj", units=0.3))
    settle(controller)
    curve = controller.run(
        "curve.create",
        dict(engine="ROUTED", points=[dict(position=p) for p in [[-1, 0, 0], [1, 0, 0]]]),
    )
    settle(controller)
    controller.selection_view.select(curve)
    controller.authoring.setEditing(True)
    settle(controller)
    return curve


def controls(controller, engine, key):
    window = engine.rootObjects()[0]
    find(window, "routingObstacleToggle").setProperty("checked", True)
    settle(controller)
    item = controller.session.document.object(key)
    assert item.engine_settings.obstacle_mode == "AUTO" and item.result.status == "ready", (
        item.result.error
    )
    assert controller.path_model.wanted
    rows = controller.authoring.componentRows
    assert len(rows) == 2 and all(r["part"] == "position" for r in rows)
    return rows[0]


def edit(controller, key, component):
    revision = controller.session.document.revision
    controller.authoring.selectComponent(component["key"], False)
    assert controller.session.document.revision == revision
    before = controller.session.document.object(key).points
    assert controller.viewport_view.beginTransform("Move")
    controller.viewport_view.transformDelta([0, 0.1, 0, 0, 0, 0, 1, 1, 1])
    controller.viewport_view.endTransform(False)
    settle(controller)
    assert controller.session.document.object(key).result.status == "ready"
    controller.run("undo", {})
    settle(controller)
    assert controller.session.document.object(key).points == before


def run():
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        key = setup(controller)
        edit(controller, key, controls(controller, engine, key))
        assert not warnings, warnings
        print("Offscreen routing controls, authored-point editing, undo and staged path passed.")
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
