"""Exercise tissue relaxation and region controls in the full offscreen desktop."""

from pathlib import Path

from PySide6.QtCore import QMetaObject, Qt
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
from ui_acceptance import find


def inspect(controller, window):
    exercise(controller, window)
    target = controller.selection
    controller.run("tissue.inflation", dict(target=target, changes=dict(mode="NORMAL")))
    settle(controller)
    click(window, "InflationToggle")
    click(window, "RelaxationToggle")
    combo = find(window, "tissueRelaxationMode")
    combo.setProperty("currentIndex", 2)
    assert QMetaObject.invokeMethod(combo, "activated", Qt.DirectConnection, argument(2))
    settle(controller)
    assert controller.session.document.object(target).relaxation.mode == "STATIC_PBD"
    regions(controller, window)


def argument(value):
    from PySide6.QtCore import Q_ARG

    return Q_ARG(int, value)


def click(window, name):
    assert QMetaObject.invokeMethod(find(window, name), "clicked", Qt.DirectConnection)


def regions(controller, window):
    click(window, "RelaxationToggle")
    click(window, "ConstraintsToggle")
    find(window, "tissueRegionMask").setProperty("currentIndex", 2)
    click(window, "tissueRegionAdd")
    settle(controller)
    item = controller.session.document.object(controller.selection)
    assert len(item.constraints) == 1 and item.constraints[0].mask == "BOUNDARY"
    assert item.intrinsic_result.status == "ready"
    assert window.grabWindow().save(str(Path("build/022-tissue/regions-inspector.png")))
    click(window, "tissueRegionRemove")
    settle(controller)
    assert not controller.session.document.object(controller.selection).constraints


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(inspect)
            print("Offscreen relaxation, source-region editing and removal passed.")
        finally:
            delete(app)
