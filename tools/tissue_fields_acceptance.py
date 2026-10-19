"""Exercise the actual field editor with offscreen QML controls."""

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
    click(window, "tissueFieldEdit")
    controller.authoring.selectAllComponents(True)
    click(window, "tissueFieldAssign")
    settle(controller)
    assert set(controller.session.document.object(controller.selection).fields[0].values) == {1}
    assert controller.authoring.transformData.get("readonly") is not False
    remove(controller, window)


def remove(controller, window):
    click(window, "tissueFieldRemove")
    settle(controller)
    assert not controller.session.document.object(controller.selection).fields


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
