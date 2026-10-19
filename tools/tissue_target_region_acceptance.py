"""Exercise target-relative region capture and unlink in the full offscreen inspector."""

from pathlib import Path

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
    target = controller.selection
    controller.run("tissue.inflation", dict(target=target, changes=dict(mode="NORMAL")))
    settle(controller)
    click(window, "InflationToggle")
    click(window, "ConstraintsToggle")
    find(window, "tissueRegionMask").setProperty("currentIndex", 2)
    click(window, "tissueRegionAdd")
    settle(controller)
    click(window, "tissueRegionBind")
    settle(controller)
    check(controller, window, target)


def check(controller, window, target):
    item = controller.session.document.object(target)
    assert item.constraints[0].reference.role == "SCP_GEOMETRY"
    assert item.intrinsic_result.status == "ready", item.intrinsic_result.error
    assert item.constraints[0].binding_asset
    assert window.grabWindow().save(str(Path("build/022-tissue/target-region-inspector.png")))
    click(window, "tissueRegionUnlink")
    settle(controller)
    assert controller.session.document.object(target).constraints[0].reference is None
    controller.run("undo", {})
    settle(controller)
    assert (
        controller.session.document.object(target).constraints[0].reference
        == item.constraints[0].reference
    )


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(inspect)
            print("Offscreen target-region capture, unlink and undo passed.")
        finally:
            delete(app)
