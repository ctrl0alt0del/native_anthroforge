"""Full-QML support draft acceptance/cancellation without desktop input."""

from tissue_parts_acceptance import activate
from tissue_stacking_acceptance import (
    QFont,
    QFontDatabase,
    QQuickStyle,
    assembly,
    click,
    delete,
    find,
    native_runtime,
    profiler_application,
    reveal,
    run,
    settle,
)


def exercise(controller, window):
    _, provider, target = assembly(controller.session)
    controller.refresh()
    controller.selection_view.select(target)
    settle(controller)
    click(window, "StackingToggle")
    click(window, "tissueStackChoice_" + provider)
    activate(window, "tissueStackOrder", 2)
    click(window, "tissueStackRegion")
    assert controller.tissue_region_tools.state["active"]
    before = controller.session.document
    click(window, "tissueStackRegionCancel")
    assert controller.session.document == before
    accept(controller, window)


def accept(controller, window):
    click(window, "tissueStackRegion")
    for _ in range(8):
        controller.render_model.drain()
        controller.frame_presented()
    controller.tissue_region_tools.probe([0.013, 0.019, 2], [0, 0, -1], True)
    assert controller.tissue_region_tools.selected
    reveal(find(window, "tissueStackRegionAccept"))
    click(window, "tissueStackRegionAccept")
    settle(controller)
    assert controller.session.document.object(controller.selection).stack_relationships[0].regions


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(exercise)
            print("Offscreen support-region draft, cancel, native pick and accept passed.")
        finally:
            delete(app)
