"""Selection-mask lifetime, staged replacement and paired orbit measurements."""

from time import perf_counter

from primitive_acceptance import settle
from primitive_performance import edit_and_measure, setup
from PySide6.QtCore import QObject, QPoint, QPointF, Qt
from PySide6.QtTest import QTest
from ui_acceptance import find
from usability_acceptance import screenshot

from anthroforge.core.metrics import Metrics


def mask_count(window):
    return len([o for o in window.findChildren(QObject) if o.objectName().startswith("mask_")])


def orbit(controller, window, enabled):
    find(window, "selectionOutline").setVisible(enabled)
    controller.cameraRequested.emit([0, 0, 0, -18, 25, 0, 3], False)
    QTest.qWait(250)
    controller.session.scheduler.metrics = Metrics()
    controller.last_frame = perf_counter()
    viewport = find(window, "viewport")
    start = viewport.mapToScene(QPointF(viewport.width() * 0.7, viewport.height() * 0.6)).toPoint()
    QTest.mousePress(window, Qt.MouseButton.RightButton, pos=start)
    for step in range(60):
        QTest.mouseMove(window, start + QPoint(step * 2, step // 2), 16)
        QTest.qWait(12)
    QTest.mouseRelease(window, Qt.MouseButton.RightButton, pos=start + QPoint(118, 29))
    return controller.session.scheduler.metrics.report()


def verify(controller, window):
    hide_context(controller)
    entity, cage = setup(controller)
    controller.selection_view.select(entity)
    controller.authoring.setEditing(False)
    controller.viewport_view.frameSelection()
    settle(controller)
    baseline = orbit(controller, window, False)
    outlined = orbit(controller, window, True)
    controller.session.scheduler.metrics = Metrics()
    retained = edit_and_measure(controller, entity, cage)
    screenshot(window, "large-outlined-replacement")
    check_staging(controller, window, retained)
    return dict(without_outline=baseline, with_outline=outlined)


def hide_context(controller):
    controller.run(
        "workspace.update", dict(hidden=[e.id for e in controller.session.document.entities])
    )


def check_staging(controller, window, retained):
    assert retained
    assert mask_count(window) == len(controller.render_model.rows), (
        mask_count(window),
        len(controller.render_model.rows),
    )
    controller.run("scp.delete", dict(entity=controller.selection))
    settle(controller)
    assert mask_count(window) == len(controller.render_model.rows)
    controller.run("undo", {})
    settle(controller)
    assert mask_count(window) == len(controller.render_model.rows)
