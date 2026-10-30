"""Parameter controls reuse native selection and component gestures without tissue transforms."""

import numpy as np

from anthroforge.desktop import authoring_actions
from tests.test_tissue_interaction import controller as controller
from tests.test_tissue_workflow import assembly


def control(controller):
    _, _, target = assembly(controller.session)
    controller.run("tissue.inflation", dict(target=target, changes=dict(mode="CTRL_POINT")))
    controller.session.wait()
    controller.refresh()
    controller.selection_view.select(target)
    before = controller.session.document
    controller.authoring.editTissueControl("main", "a")
    assert controller.session.document == before
    assert controller.authoring.selectedComponent["part"] == "tissue_control"
    return target


def test_control_gesture_commits_once_and_keeps_generated_tissue_nontransformable(controller):
    target = control(controller)
    editor, session = controller.authoring, controller.session
    start, cursor = np.asarray(editor.selectedPoints[0]), session.history.cursor
    assert editor.transformData["transformable"]
    assert not controller.selection_view.selectedData["transformable"]
    authoring_actions.start_transform(editor, "Move")
    authoring_actions.transform_delta(editor, [0, 0, 0.03, 0, 0, 0, 1, 1, 1])
    session.commit()
    session.wait()
    value = session.document.object(target).parts[0].a.inflation.control
    np.testing.assert_allclose(value, start + [0, 0, 0.03], atol=1e-12)
    assert session.history.cursor == cursor + 1
    assert_control_undo(session, target)


def assert_control_undo(session, target):
    session.command("undo")
    session.wait()
    assert not session.document.object(target).parts[0].a.inflation.control


def test_cancel_control_drag_restores_parameters_and_selection_is_nonmutating(controller):
    target = control(controller)
    before, editor = controller.session.document.object(target), controller.authoring
    authoring_actions.start_transform(editor, "Move")
    authoring_actions.transform_delta(editor, [0.02, 0, 0, 0, 0, 0, 1, 1, 1])
    controller.session.cancel()
    controller.session.wait()
    assert controller.session.document.object(target).parts == before.parts
