"""Material weights are edited without moving generated vertices or reinterpreting indices."""

import numpy as np
import pytest

from anthroforge.desktop import authoring_actions
from tests.test_tissue_interaction import controller as controller
from tests.test_tissue_workflow import assembly, roundtrip


def create(session, target, name="pins", domain="BASE"):
    session.command("tissue.field.create", target=target, name=name, domain=domain)
    session.wait()
    return session.document.object(target).fields[-1]


def test_weight_assignment_is_explicit_atomic_and_persistent(session, tmp_path):
    _, _, target = assembly(session)
    field = create(session, target)
    assign(session, target, field.topology, [0, 3], 0.7)
    session.wait()
    weights = session.document.object(target).fields[0].values
    assert weights[0] == weights[3] == 0.7 and weights[1] == 0
    roundtrip(session, tmp_path / "fields.anthroforge")
    assert session.document.object(target).fields[0].values == weights


@pytest.mark.parametrize(
    "stale,indices,value", [(True, [0], 1), (False, [-1], 1), (False, [0], 1.1)]
)
def test_stale_indices_and_invalid_assignment_do_not_change_state(session, stale, indices, value):
    _, _, target = assembly(session)
    field = create(session, target)
    before = session.document
    with pytest.raises(ValueError):
        assign(session, target, "old" if stale else field.topology, indices, value)
    assert session.document == before


def assign(session, target, topology, indices, value):
    session.command(
        "tissue.field.assign",
        target=target,
        name="pins",
        indices=indices,
        value=value,
        topology=topology,
    )


def test_field_components_pick_and_assign_with_undo_without_vertex_transforms(controller):
    _, _, target = assembly(controller.session)
    field = create(controller.session, target, domain="REST")
    controller.refresh()
    controller.selection_view.select(target)
    controller.authoring.editTissueField("pins")
    editor, before = controller.authoring, controller.session.document
    assert len(editor.componentRows) == len(field.values)
    editor.selectComponent(editor.componentRows[0]["key"], False)
    assert editor.transformData["readonly"]
    with pytest.raises(ValueError, match="weights|coordinates"):
        authoring_actions.start_transform(editor, "Move")
    assert controller.session.document == before
    assign_and_undo(controller, target)


def assign_and_undo(controller, target):
    controller.authoring.assignTissueWeight(0.5)
    controller.session.wait()
    assert controller.session.document.object(target).fields[0].values[0] == 0.5
    controller.run("undo", {})
    controller.session.wait()
    np.testing.assert_array_equal(controller.session.document.object(target).fields[0].values, 0)
