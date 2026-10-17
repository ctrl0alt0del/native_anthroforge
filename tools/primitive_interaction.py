"""Real viewport pointer interaction plus imported/body editing and topology UI policies."""

from pathlib import Path

import numpy as np
from primitive_acceptance import screenshot, settle
from PySide6.QtCore import Q_ARG, Q_RETURN_ARG, QMetaObject, QPointF, Qt
from PySide6.QtTest import QTest
from ui_acceptance import find


def pointer(window, world, click=False, extend=False):
    viewport = find(window, "viewport")
    point = QMetaObject.invokeMethod(
        viewport,
        "projectPoint",
        Q_RETURN_ARG(QPointF),
        *(Q_ARG(float, float(value)) for value in world),
    )
    position = viewport.mapToScene(point).toPoint()
    QTest.mouseMove(window, position)
    QTest.qWait(100)
    if click:
        modifier = Qt.KeyboardModifier.ControlModifier if extend else Qt.KeyboardModifier.NoModifier
        QTest.mouseClick(window, Qt.MouseButton.LeftButton, modifier, position)
        QTest.qWait(100)


def curve_selection(controller, window, entity):
    controller.select(entity)
    controller.authoring.setEditing(True)
    pointer(window, [0, -0.15, 0])
    assert controller.authoring.hover_curve
    predicted = controller.authoring.hover_curve
    pointer(window, [0, -0.15, 0], True)
    assert len(controller.authoring.selection) == 2
    assert all(predicted in key for key in controller.authoring.selection)
    pointer(window, [0.25, 0.15, 0], True, True)
    assert len(controller.authoring.selection) == 4
    screenshot(window, "curve-selection")


def topology_controls(controller, window, entity):
    child = controller.run("scp.empty", dict(name="Topology dependent", parent=entity))
    controller.select(entity)
    settle(controller)
    assert not find(window, "primitiveSamples").isEnabled()
    controller.run("scp.delete", dict(entity=child))
    settle(controller)
    assert find(window, "primitiveSamples").isEnabled()
    control = controller.run("control.create", dict(entity=entity))
    controller.run("control.attach", dict(control=control, support=entity))
    settle(controller)
    assert not find(window, "primitiveSamples").isEnabled()
    controller.run("control.follow", dict(control=control, entity=entity))
    settle(controller)
    assert find(window, "primitiveSamples").isEnabled()


def imported_hook(controller, window, parent):
    source = Path("examples/primitives/cube.obj").resolve()
    imported = controller.run("import", dict(path=str(source), units=1, parent=parent))
    settle(controller)
    entity = imported["entity_id"]
    controller.select(entity)
    controller.authoring.setEditing(True)
    original = source_vertices(controller, entity)
    controller.authoring.selectComponent(controller.authoring.componentRows[0]["key"], False)
    controller.authoring.addDeformer("HOOK")
    settle(controller)
    control = controller.selection
    verify_imported_weight(controller, entity, control, original)
    screenshot(window, "imported-hook")
    return entity


def verify_imported_weight(controller, entity, control, original):
    controller.select(entity)
    binding = controller.session.document.entity(entity).deformers[0].id
    controller.authoring.members(binding, False)
    controller.authoring.weights(binding, 0.25)
    controller.select(control)
    controller.beginTransform("Move")
    controller.dragTransform(2, 0.4)
    controller.endTransform(False)
    settle(controller)
    assert_imported_shape(controller, entity, original)


def source_vertices(controller, entity):
    key = controller.session.document.entity(entity).primitive.source
    return controller.session.assets[key].mesh.array(0).copy()


def assert_imported_shape(controller, entity, original):
    item = controller.session.document.entity(entity)
    np.testing.assert_array_equal(
        controller.session.assets[item.primitive.source].mesh.array(0), original
    )
    result = controller.session.assets[item.asset].mesh.array(0)
    np.testing.assert_allclose(result[0] - original[0], [0, 0, 0.1], atol=1e-7)
    np.testing.assert_allclose(result[1:], original[1:], atol=1e-7)


def body_base_hook(controller, window, parent):
    controller.select(parent)
    controller.authoring.create("BODY", "CAPSULE")
    settle(controller)
    entity = controller.selection
    controller.authoring.setCategory("BASE")
    controller.authoring.selectComponent(controller.authoring.componentRows[0]["key"], False)
    controller.authoring.addDeformer("HOOK")
    settle(controller)
    item = controller.session.document.entity(entity)
    assert item.deformers[0].target.stage == "BASE"
    controller.select(entity)
    controller.authoring.setCategory("CURVE")
    isolate_body(controller, entity)
    screenshot(window, "body-base-hook")


def isolate_body(controller, entity):
    others = [e.id for e in controller.session.document.entities if e.id != entity]
    controller.run("workspace.update", dict(hidden=others))
    controller.frameSelection()
    settle(controller)


def component_presentation(controller, window, entity):
    controller.select(entity)
    row = controller.authoring.componentRows[-2]
    controller.authoring.selectComponent(row["key"], False)
    QTest.qWait(50)
    assert find(window, "curveChoice").property("currentIndex") == 1
    assert find(window, "pointChoice").property("currentIndex") == 1
    controller.run("workspace.update", dict(hidden=[entity]))
    assert not controller.authoring.visible
    controller.run("workspace.update", dict(hidden=[], unpickable=[entity]))
    assert not controller.authoring.pick([0, 0, 2], [0, 0, -1], 10, 0, True, False)
    controller.run("workspace.update", dict(unpickable=[]))


def followed_control_drag(controller, entity):
    from anthroforge.application.control_frames import stable_frame

    parent = controller.run("scp.empty", dict(name="Rotated support", parent=entity))
    controller.run("scp.transform", dict(entity=parent, values=[0, 0, 0, 0, 0, 90, 1, 1, 1]))
    control = controller.run("control.create", dict(entity=parent))
    controller.select(control)
    before = stable_frame(controller.session, controller.session.document.control(control))
    controller.beginTransform("Move")
    controller.dragTransform(0, 0.2)
    controller.endTransform(False)
    settle(controller)
    after = stable_frame(controller.session, controller.session.document.control(control))
    verify_world_translation(controller, before, after)
    verify_control_undo(controller, control, before)


def verify_world_translation(controller, before, after):
    before_position = controller.session.engine.decompose(before)[:3]
    after_position = controller.session.engine.decompose(after)[:3]
    np.testing.assert_allclose(np.subtract(after_position, before_position), [0.2, 0, 0], atol=1e-7)


def verify_control_undo(controller, control, before):
    from anthroforge.application.control_frames import stable_frame

    controller.run("undo", {})
    settle(controller)
    np.testing.assert_allclose(
        stable_frame(controller.session, controller.session.document.control(control)), before
    )


def editing_policies(controller, window, entity):
    component_presentation(controller, window, entity)
    topology_controls(controller, window, entity)
    followed_control_drag(controller, entity)


def verify(controller, window):
    controller.authoring.create("LOFT", "")
    settle(controller)
    entity = controller.selection
    controller.frameSelection()
    QTest.qWait(150)
    curve_selection(controller, window, entity)
    editing_policies(controller, window, entity)
    imported_hook(controller, window, entity)
    body_base_hook(controller, window, entity)
    assert not controller.session.scheduler.errors, controller.session.scheduler.errors
    return dict(
        pointer_selection=True, topology_ui=True, imported_weights=True, body_base_hook=True
    )
