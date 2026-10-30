"""Full QML sampling controls and base component agreement, without desktop windows."""

from PySide6.QtCore import Q_ARG, QMetaObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from surface_editor_acceptance import action, settle
from ui_acceptance import find

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime


def exercise(controller, engine):
    target = controller.run("primitive.create", dict(kind="BODY", shape="BOX"))
    settle(controller)
    controller.selection_view.select(target)
    controller.authoring.setEditing(True)
    settle(controller)
    window = engine.rootObjects()[0]
    find(window, "curveSampleOverride").setProperty("checked", True)
    action(engine, "curveSampleOverride", "clicked")
    settle(controller)
    control = find(window, "curveSamples")
    assert QMetaObject.invokeMethod(control, "edited", Qt.DirectConnection, Q_ARG(float, 12.0))
    settle(controller)
    verify_components(controller, engine, target)


def verify_components(controller, engine, target):
    item = controller.session.document.entity(target)
    assert item.primitive.curves[0].samples == 12, (item.primitive.curves, controller.message)
    controller.authoring.setCategory("BASE")
    settle(controller)
    assert len(controller.authoring.componentRows) == 48
    child = controller.run("scp.empty", dict(name="Child", parent=target))
    controller.selection_view.select(target)
    settle(controller)
    assert not find(engine.rootObjects()[0], "curveSamples").isEnabled()
    controller.run("scp.delete", dict(entity=child))
    settle(controller)
    assert find(engine.rootObjects()[0], "curveSamples").isEnabled()


def run():
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        exercise(controller, engine)
        assert not warnings, warnings
        assert not controller.message, controller.message
        print("Offscreen consumer sampling, base components and topology locks passed.")
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
