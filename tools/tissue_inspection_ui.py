"""Offscreen controls, direct stage switching, point mode and explicit geometry checks."""

from pathlib import Path

from PySide6.QtCore import Q_ARG, QMetaObject, Qt
from PySide6.QtQuickControls2 import QQuickStyle
from tissue_editor_acceptance import exercise, run, settle
from ui_acceptance import find

from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime


def activate(window, name, index):
    combo = find(window, name)
    combo.setProperty("currentIndex", index)
    assert QMetaObject.invokeMethod(combo, "activated", Qt.DirectConnection, Q_ARG(int, index))


def inspect(controller, window):
    exercise(controller, window)
    before = controller.session.document
    compare_stages(window)
    settle(controller)
    assert controller.tissue_inspection.summary["state"] == "ready"
    click(window, "tissueExplainPoint")
    assert controller.tissue_inspection.armed
    click(window, "tissueCheckGeometry")
    settle(controller)
    assert controller.session.document is before
    assert window.grabWindow().save("build/tissue-inspection/inspector.png")


def compare_stages(window):
    click(window, "inspectTab")
    find(window, "tissueInspectionPanel").setProperty("expanded", True)
    activate(window, "tissueInspectStage", 2)
    activate(window, "tissueInspectReference", 1)
    activate(window, "tissueInspectMode", 1)


def click(window, name):
    assert QMetaObject.invokeMethod(find(window, name), "clicked", Qt.DirectConnection)


if __name__ == "__main__":
    Path("build/tissue-inspection").mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        run(inspect)
    print("Offscreen inspection controls and unchanged anatomy passed.")
