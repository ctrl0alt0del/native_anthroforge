"""Full-QML draft, accept and cancel without touching desktop input."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from numeric_input_acceptance import reveal
from PySide6.QtCore import Q_ARG, QMetaObject, Qt
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


def amount(window, value):
    assert QMetaObject.invokeMethod(
        find(window, "tissueInflationAmount"), "edited", Qt.DirectConnection, Q_ARG(float, value)
    )


def inspect(controller, window):
    exercise(controller, window)
    target, cursor = controller.selection, controller.session.history.cursor
    before = controller.session.document
    reveal(window, "tissuePreviewStart")
    click(window, "tissuePreviewStart")
    amount(window, 0.08)
    settle(controller)
    assert controller.tissuePreview["state"] == "ready"
    assert controller.session.document == before
    assert controller.session.history.cursor == cursor
    assert any(row["id"].startswith("preview:") for row in controller._render_rows)
    assert window.grabWindow().save("build/022-tissue/inflation-preview-inspector.png")
    finish(controller, window, target, cursor)


def finish(controller, window, target, cursor):
    click(window, "tissuePreviewCancel")
    settle(controller)
    assert not any(row["id"].startswith("preview:") for row in controller._render_rows)
    click(window, "tissuePreviewStart")
    amount(window, 0.05)
    settle(controller)
    click(window, "tissuePreviewAccept")
    settle(controller)
    assert controller.session.document.object(target).parts[0].a.inflation.amount == 0.05
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    settle(controller)
    assert controller.session.document.object(target).parts[0].a.inflation.amount != 0.05


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(inspect)
            print("Offscreen inflation preview, draft, acceptance, cancellation and undo passed.")
        finally:
            delete(app)
