"""Hidden reconstruction navigation qualification; no desktop input or visible windows."""

import json
import os
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEvent, QObject, QSizeF, QUrl
from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtQml import QQmlComponent
from PySide6.QtQuickControls2 import QQuickStyle

from anthroforge.desktop import offscreen, runtime
from anthroforge.desktop.controller import Controller

OUTPUT = Path("build/reconstruction-042/gui")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(OUTPUT / "preferences.json")
    build = Path(os.environ.get("AF_NATIVE_BUILD", "build/dev")).resolve()
    runtime.build_directory = offscreen.build_directory = lambda: build
    app = QGuiApplication([])
    QQuickStyle.setStyle("Basic")
    with runtime.native_runtime():
        run(app)


def run(app):
    controller, warnings = Controller(), []
    controller.timer.stop()
    renderer = offscreen.Offscreen(controller, warnings)
    renderer.window.setColor(QColor("#2b2c30"))
    try:
        fixture(controller)
        panel(app, controller, renderer)
        review(app, controller, renderer)
        comparison(app, controller, renderer)
        assert not renderer.window.isVisible() and not warnings, warnings
        (OUTPUT / "result.json").write_text(json.dumps(dict(warnings=warnings, visible=False)))
    finally:
        renderer.close()
        controller.close()


def fixture(controller):
    session = controller.session
    target = session.command("import", path="examples/primitives/cube.obj", units=1)["entity_id"]
    session.wait()
    controller.refresh()
    controller.selection_view.select(target)
    controller.reconstruction_panel.create()
    controller.reconstruction_panel.run("variant.checkpoint", {"name": "Initial alternative"})
    populate(session, target)


def populate(session, target):
    variant = session.contexts.visible
    kind = session.command("catalogue.type.create", name="Sternocleidomastoid", category="Muscle")
    session.command("catalogue.assign", target=target, type_id=kind, variant=variant, side="LEFT")
    session.command(
        "catalogue.region.set",
        name="Attachment footprint",
        target=target,
        variant=variant,
        triangles=[0, 1],
    )
    session.command("catalogue.collection.set", name="Neck reconstruction", members=[target])
    populate_review(session, target, variant)
    session.command("reconstruction.queue.add", subject=target, variant=variant, type_id=kind)


def populate_review(session, target, variant):
    session.command(
        "review.set",
        subject=target,
        variant=variant,
        dimension="ANATOMY",
        decision="APPROVED",
        reviewer="Qualification",
        comment="Independent shape review with retained stage provenance.",
    )


def panel(app, controller, renderer):
    path = Path("src/anthroforge/desktop/qml/ReconstructionPane.qml").resolve()
    component = QQmlComponent(renderer.engine)
    component.setData(path.read_bytes(), QUrl.fromLocalFile(str(path)))
    item = component.create()
    assert item is not None, [e.toString() for e in component.errors()]
    renderer.root.setVisible(False)
    item.setParentItem(renderer.window.contentItem())
    for height in (400, 700, 960):
        item.setSize(QSizeF(360, height))
        capture_pages(app, controller, renderer, height, item)
    release(item)


def capture_pages(app, controller, renderer, height, item):
    for page in ("Variants", "Catalogue", "Regions", "Stages", "Reviews", "Queue"):
        controller.reconstruction_panel.setPage(page)
        for _ in range(5):
            app.processEvents()
            image = renderer.frame()
        if page == "Variants":
            view = item.findChild(QObject, "variantList")
            assert view and view.property("height") >= 150 and view.property("count") >= 2
        assert image.save(str(OUTPUT / (page.lower() + f"-{height}.png")))


def comparison(app, controller, renderer):
    panel = controller.reconstruction_compare
    panel.inspect(controller.selection)
    controller.session.reconstruction_comparison.wait(60)
    panel.synchronize()
    path = review_wrapper("ReconstructionCompareDialog")
    component = QQmlComponent(renderer.engine)
    component.setData(path.read_bytes(), QUrl.fromLocalFile(str(path)))
    item = component.create()
    assert item is not None, [e.toString() for e in component.errors()]
    render_review(app, controller, renderer, item, "comparison.png")


def review(app, controller, renderer):
    key = controller.session.contexts.visible
    controller.variant_panel.inspect(key, "promote")
    controller.session.variant_review.wait(60)
    controller.variant_panel.synchronize()
    path = review_wrapper()
    component = QQmlComponent(renderer.engine)
    component.setData(path.read_bytes(), QUrl.fromLocalFile(str(path)))
    item = component.create()
    assert item is not None, [e.toString() for e in component.errors()]
    render_review(app, controller, renderer, item)


def review_wrapper(dialog="VariantReviewDialog"):
    path = (OUTPUT / ("Capture" + dialog + ".qml")).resolve()
    qml = Path("src/anthroforge/desktop/qml").resolve().as_uri()
    body = "Item { Components." + dialog + " { Component.onCompleted: open() } }"
    path.write_text('import QtQuick\nimport "' + qml + '" as Components\n' + body)
    return path


def render_review(app, controller, renderer, item, filename="promotion.png"):
    item.setSize(QSizeF(1280, 960))
    item.setParentItem(renderer.window.contentItem())
    for _ in range(12):
        app.processEvents()
        controller.process_tick()
        image = renderer.frame()
        controller.frame_presented()
    assert image.save(str(OUTPUT / filename))
    release(item)


def release(item):
    item.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


if __name__ == "__main__":
    main()
