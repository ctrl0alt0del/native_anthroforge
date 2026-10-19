"""Full QML structural protection controls and accepted surface updates, offscreen only."""

from pathlib import Path

from PySide6.QtCore import QMetaObject, QPointF, Qt
from PySide6.QtGui import QFont, QFontDatabase
from tissue_editor_acceptance import (
    QQuickStyle,
    delete,
    native_runtime,
    profiler_application,
    run,
    scene,
    settle,
)
from ui_acceptance import find


def exercise(controller, window):
    scene(controller)
    membrane = controller.session.document.object(controller.selection)
    fiber = membrane.curves[0].curve
    controller.select(fiber)
    controller.authoring.setEditing(True)
    settle(controller)
    for name, attribute in (
        ("pointStackingFixed", "stacking_fixed"),
        ("pointProtectedCrease", "protected_crease"),
    ):
        toggle(controller, window, fiber, name, attribute)
    reveal(find(window, "pointStackingFixed"))
    settle(controller)
    assert window.grabWindow().save(str(Path("build/022-tissue/structural-pins-inspector.png")))


def reveal(control):
    parent = control.parentItem()
    while parent is not None:
        if parent.metaObject().indexOfProperty("contentY") >= 0:
            item = parent.property("contentItem")
            position = control.mapToItem(item, QPointF(0, 0))
            maximum = parent.property("contentHeight") - parent.height()
            parent.setProperty("contentY", max(0, min(position.y() - 220, maximum)))
            return
        parent = parent.parentItem()


def toggle(controller, window, fiber, name, attribute):
    control = find(window, name)
    assert control.property("visible") and control.property("enabled")
    control.setProperty("checked", True)
    assert QMetaObject.invokeMethod(control, "clicked", Qt.DirectConnection)
    settle(controller)
    assert getattr(controller.session.document.object(fiber).points[0], attribute)
    controller.run("undo", {})
    settle(controller)
    assert not getattr(controller.session.document.object(fiber).points[0], attribute)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(exercise)
            print("Offscreen structural point protection and one-action undo passed.")
        finally:
            delete(app)
