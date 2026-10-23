"""Generated-point references retain their parameter meaning across all writers."""

import numpy as np
import pytest

from tests.test_driving_formulas import driver, reference, result
from tests.test_parametric_curves import create
from tests.test_parametric_deformation import body_and_hook


def resize(session, curve, count, operation="curve.parametric.configure"):
    if operation == "curve.parametric.configure":
        session.command(operation, curve=curve, changes=dict(resolution=count))
    else:
        session.command(operation, reference=reference(curve), value=count)


@pytest.mark.parametrize(
    "operation", ["curve.parametric.configure", "property.set", "shortcut.set"]
)
@pytest.mark.parametrize("enabled", [True, False])
def test_restricted_binding_blocks_all_writers_until_removed(session, operation, enabled):
    curve, _, _, binding = body_and_hook(session, restricted=True)
    session.command("deformer.update", binding=binding, enabled=enabled)
    session.wait(5)
    before = session.document
    with pytest.raises(ValueError, match="membership"):
        resize(session, curve, 9, operation)
    assert session.document == before
    session.command("deformer.remove", binding=binding)
    resize(session, curve, 9, operation)
    session.wait(5)
    assert len(session.document.object(curve).points) == 9


@pytest.mark.parametrize("kind", ["HOOK", "LATTICE"])
def test_point_weights_lock_and_clearing_weights_unlocks(session, kind):
    curve, body, _, _ = body_and_hook(session)
    control = session.command("control.create", entity=body, kind=kind)
    binding = session.command(
        "deformer.add",
        control=control,
        target=dict(owner=body, stage="CURVE", component=curve),
        weights=[0.5] * 15,
    )
    with pytest.raises(ValueError, match="weights"):
        resize(session, curve, 9)
    session.command("deformer.update", binding=binding, weights=[])
    resize(session, curve, 9)
    session.wait(5)
    assert len(session.document.object(curve).points) == 9


def point_formula(session, curve, input_reference):
    point = session.document.object(curve).points[-1].id
    ref = reference(curve, ("points", "@" + point, "radius"))
    other = session.command("curve.create")
    session.wait(5)
    if input_reference:
        return driver(session, other, "floor(r)", inputs=[dict(name="r", property=ref)])
    return driver(session, curve, "value", value=1.0, path=ref)


@pytest.mark.parametrize("input_reference", [True, False])
@pytest.mark.parametrize("enabled", [True, False])
def test_formula_point_targets_and_inputs_lock_until_reference_removed(
    session, input_reference, enabled
):
    curve = create(session, resolution=5)
    key, formula = point_formula(session, curve, input_reference)
    session.command(
        "driver.formula.update", driver=key, formula=formula, changes=dict(enabled=enabled)
    )
    with pytest.raises(ValueError, match="generated-point formula references"):
        resize(session, curve, 9)
    session.command("driver.formula.remove", driver=key, formula=formula)
    resize(session, curve, 9)
    session.wait(5)
    assert len(session.document.object(curve).points) == 9


def test_resolution_driver_retains_accepted_geometry_when_membership_blocks_update(session):
    curve, _, _, binding = body_and_hook(session, restricted=True)
    key, formula = driver(session, curve, "value", value=5, kind="INTEGER")
    session.wait(5)
    before = path_snapshot(session, curve)
    session.command("driver.value", driver=key, value=9)
    session.wait(5)
    assert result(session, formula).status == "failed"
    assert "membership" in result(session, formula).error
    assert_retained(before, path_snapshot(session, curve))
    session.command("deformer.remove", binding=binding)
    session.command("driver.value", driver=key, value=11)
    session.wait(5)
    assert len(session.document.object(curve).points) == 11
    assert result(session, formula).status == "ready"


def assert_retained(before, after):
    assert before[0].points == after[0].points
    assert before[0].engine_settings == after[0].engine_settings
    np.testing.assert_array_equal(before[1], after[1])


def path_snapshot(session, curve):
    item = session.document.object(curve)
    return item, session.resources.paths[item.result.asset].path.array().copy()


def test_property_inspection_explains_lock_without_locking_unrelated_curve(session):
    curve, _, _, binding = body_and_hook(session, restricted=True)
    other = create(session, resolution=5)
    info = session.command("property.get", reference=reference(curve))
    assert not info["writable"] and "remove its deformer binding" in info["reason"]
    assert session.command("property.get", reference=reference(other))["writable"]
    resize(session, curve, 5)
    session.command("deformer.remove", binding=binding)
    assert session.command("property.get", reference=reference(curve))["writable"]
    session.command("undo")
    assert not session.command("property.get", reference=reference(curve))["writable"]


def test_restoring_definition_cannot_bypass_point_membership_lock(session):
    curve, _, _, _ = body_and_hook(session, restricted=True)
    session.command("curve.engine", curve=curve, engine="BEZIER")
    session.wait(5)
    session.command("curve.point.insert", curve=curve, index=1, point=dict(position=[0.1, 0, 0]))
    session.wait(5)
    before = session.document.object(curve)
    with pytest.raises(ValueError, match="membership"):
        session.command("curve.engine", curve=curve, engine="PARAMETRIC")
    assert session.document.object(curve) == before
