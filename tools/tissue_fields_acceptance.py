"""Exercise the actual field editor with offscreen QML controls."""

from PySide6.QtCore import Q_ARG, QMetaObject, Qt
from tissue_editor_acceptance import (
    QFont,
    QFontDatabase,
    QQuickStyle,
    delete,
    exercise,
    native_runtime,
    profiler_application,
    run,
    settle,
)
from tissue_relaxation_acceptance import click
from ui_acceptance import find


def fields(controller, window):
    exercise(controller, window)
    click(window, "InflationToggle")
    click(window, "Weight fieldsToggle")
    find(window, "tissueFieldName").setProperty("text", "Test pins")
    click(window, "tissueFieldCreate")
    settle(controller)
    assert controller.authoring.editing
    controller.authoring.selectAllComponents(True)
    assign(controller, window)
    settle(controller)
    assert set(controller.session.document.object(controller.selection).fields[0].values) == {1}
    assert controller.authoring.transformData.get("readonly") is not False
    mixed(controller, window)
    remove(controller, window)


def assign(controller, window):
    before = len(controller.session.history.entries)
    field = find(window, "tissueFieldWeight")
    assert field.property("enabled")
    assert QMetaObject.invokeMethod(field, "edited", Qt.DirectConnection, Q_ARG(float, 1.0))
    settle(controller)
    assert len(controller.session.history.entries) == before + 1
    controller.run("undo", {})
    settle(controller)
    assert set(controller.session.document.object(controller.selection).fields[0].values) == {0}
    controller.run("redo", {})
    settle(controller)


def remove(controller, window):
    click(window, "tissueFieldRemove")
    settle(controller)
    assert not controller.session.document.object(controller.selection).fields


def mixed(controller, window):
    controller.authoring.setEditing(False)
    click(window, "tissueField_Test pins")
    assert controller.authoring.editing
    editor = controller.authoring
    editor.selectComponent(editor.componentRows[0]["key"], False)
    control = find(window, "tissueFieldWeight")
    QMetaObject.invokeMethod(control, "edited", Qt.DirectConnection, Q_ARG(float, 0.5))
    settle(controller)
    editor.selectAllComponents(True)
    settle(controller)
    assert control.property("mixed")
    QMetaObject.invokeMethod(control, "edited", Qt.DirectConnection, Q_ARG(float, 0.75))
    settle(controller)
    assert set(controller.session.document.object(controller.selection).fields[0].values) == {0.75}


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(fields)
            print("Field creation, component selection, weight assignment and removal passed.")
        finally:
            delete(app)
