"""Material crop desktop control and hidden-GPU empty replacement qualification."""

from PySide6.QtGui import QFont, QFontDatabase
from tissue_editor_acceptance import (
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


def inspect(controller, window):
    exercise(controller, window)
    click(window, "InflationToggle")
    click(window, "Material cropToggle")
    find(window, "tissueCropEnabled").setProperty("checked", True)
    click(window, "tissueCropEnabled")
    settle(controller)
    item = controller.session.document.object(controller.selection)
    assert item.crop.enabled and item.result.status == "ready"


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(inspect)
            print("Offscreen crop controls passed.")
        finally:
            delete(app)
