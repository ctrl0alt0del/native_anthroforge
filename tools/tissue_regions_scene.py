"""Inspect native material footprint overlays on actual displayed GPU geometry."""

from tissue_stacking_scene import (
    Controller,
    Offscreen,
    QGuiApplication,
    QQuickStyle,
    frames,
    native_runtime,
    prepare,
)


def exercise(controller, renderer, app):
    first, second = prepare(controller)
    frames(controller, renderer, app)
    tool = controller.tissue_region_tools
    tool.begin(dict(other=first, mode="EXPLICIT"))
    before = controller.session.document
    for x in (-0.1, 0, 0.1):
        for y in (-0.1, 0, 0.1):
            tool.probe([x, y, 2], [0, 0, -1], True)
    assert len(tool.selected) == 9 and tool.outline
    assert frames(controller, renderer, app).save("build/022-tissue/support-region-gpu.png")
    assert controller.session.document == before
    tool.cancel()
    assert not tool.outline


def run(app):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, app)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
        print("Hidden GPU support footprint rendering and cancellation passed.")
