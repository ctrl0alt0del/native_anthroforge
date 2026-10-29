"""Component identities and restrictions agree across curve, control and tissue domains."""

import json

import numpy as np

from tests.test_parametric_consumers import joined
from tests.test_tissue_field_editing import create as field
from tests.test_tissue_interaction import controller as controller
from tests.test_tissue_workflow import assembly as tissue_assembly


def test_parametric_and_junction_positions_explain_readonly_state(session):
    parametric, follower, joint = joined(session)
    result = session.command("editing.inspect", target=parametric)
    assert all(not r["position_editable"] for r in result["components"])
    result = session.command("editing.inspect", target=follower)
    linked = [r for r in result["components"] if r["reference"]["junction"] == joint]
    point = next(r for r in linked if r["reference"]["part"] == "position")
    assert not point["position_editable"] and "Parametric" in point["position_reason"]
    json.dumps(result, allow_nan=False)


def test_control_frame_and_imported_weights_are_exposed(session, assembly):
    bone, _ = assembly
    control = session.command("control.create", kind="LATTICE", entity=bone)
    session.wait()
    result = session.command("editing.inspect", target=control, category="CONTROL")
    assert result["components"] and all(
        r["reference"]["part"] == "lattice" for r in result["components"]
    )
    binding = session.command(
        "deformer.add", control=control, target=dict(owner=bone, stage="GEOMETRY")
    )
    session.wait()
    result = session.command("editing.inspect", target=bone, context=dict(deformer=binding))
    assert all(r["weight_editable"] and not r["position_editable"] for r in result["components"])


def test_tissue_field_points_match_desktop_and_are_weight_only(controller):
    session = controller.session
    _, _, tissue = tissue_assembly(session)
    field(session, tissue, domain="REST")
    controller.refresh()
    controller.select(tissue)
    controller.authoring.editTissueField("pins")
    result = session.command(
        "editing.inspect", target=tissue, category="TISSUE_FIELD", context=dict(field="pins")
    )
    np.testing.assert_array_equal(
        [r["world"] for r in result["components"]], [r[1] for r in controller.authoring.rows]
    )
    assert all(r["weight_editable"] and not r["position_editable"] for r in result["components"])


def test_tissue_control_query_uses_current_part_side(controller):
    session = controller.session
    _, _, target = tissue_assembly(session)
    controller.refresh()
    controller.select(target)
    controller.authoring.editTissueControl("main", "a")
    result = session.command("editing.inspect", target=target, category="TISSUE_CONTROL")
    assert [r["reference"] for r in result["components"]] == [
        r[0] for r in controller.authoring.rows
    ]


def test_primitive_consumer_query_reuses_source_points_with_consumer_frame(session):
    curve = session.command("curve.create")
    body = session.command("primitive.from_curves", curves=[curve], kind="BODY")
    session.wait()
    session.command("scp.transform", entity=body, values=[1, 2, 3, 0, 0, 0, 1, 1, 1])
    session.wait()
    rows = session.command("editing.inspect", target=body)["components"]
    assert all(r["reference"]["curve"] == curve for r in rows)
    np.testing.assert_allclose(
        np.array([r["world"] for r in rows]) - np.array([r["local"] for r in rows]),
        np.tile([1, 2, 3], (len(rows), 1)),
    )
    bases = session.command("editing.inspect", target=body, category="BASE")["components"]
    assert bases and all(not r["position_editable"] for r in bases)
