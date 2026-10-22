"""Driving formulas exercise public operations and the normal task coordinator."""

from dataclasses import asdict

import pytest

from anthroforge.application import formula_evaluation, formula_inputs
from anthroforge.core.numeric_properties import PropertyRef
from anthroforge.native.mesh import NativeCancellation


def curve(session, name="Curve"):
    target = session.command("curve.create", name=name)
    session.wait(5)
    return target


def reference(target, path=("engine_settings", "resolution"), component=None):
    return asdict(PropertyRef(target, path, component))


def driver(session, target, expression, *, inputs=None, value=0.0, kind="REAL", path=None):
    key = session.command("driver.create", value=value, numeric_type=kind)
    formula = session.command(
        "driver.formula.add",
        driver=key,
        target=path or reference(target),
        expression=expression,
        inputs=inputs,
    )
    return key, formula


def result(session, formula):
    return next(r for r in session.document.formula_results if r.formula == formula)


def test_driver_applies_natively_and_retains_value_when_disabled(session):
    target = curve(session)
    key, formula = driver(session, target, "value * 2", value=6, kind="INTEGER")
    session.wait(5)
    assert session.document.object(target).resolution == 12
    assert result(session, formula).status == "ready"
    session.command(
        "driver.formula.update", driver=key, formula=formula, changes={"enabled": False}
    )
    assert session.document.object(target).resolution == 12
    session.command("property.set", reference=reference(target), value=9)
    assert session.document.object(target).resolution == 9


def test_chain_and_independent_failure(session):
    a, b, c = curve(session, "A"), curve(session, "B"), curve(session, "C")
    key, first = driver(session, a, "value + 1", value=8, kind="INTEGER")
    _, second = driver(
        session, b, "upstream * 2", inputs=[dict(name="upstream", property=reference(a))]
    )
    _, invalid = driver(session, c, "12.0")
    session.wait(5)
    assert (session.document.object(a).resolution, session.document.object(b).resolution) == (9, 18)
    assert result(session, invalid).status == "failed"
    session.command("driver.value", driver=key, value=10)
    session.wait(5)
    assert session.document.object(b).resolution == 22
    assert result(session, first).status == result(session, second).status == "ready"


def test_cycle_retains_group_and_dependents_without_blocking_unrelated(session):
    a, b, c, d = (curve(session, label) for label in "ABCD")
    _, fa = driver(session, a, "x", inputs=[dict(name="x", property=reference(b))])
    _, fb = driver(session, b, "x", inputs=[dict(name="x", property=reference(a))])
    _, fc = driver(session, c, "x", inputs=[dict(name="x", property=reference(b))])
    _, fd = driver(session, d, "7")
    session.wait(5)
    assert [session.document.object(key).resolution for key in (a, b, c, d)] == [24, 24, 24, 7]
    assert all(result(session, key).status == "failed" for key in (fa, fb, fc))
    assert result(session, fd).status == "ready"


def test_typed_units_and_uniform_vector(session):
    target = curve(session)
    ref = reference(target, ("transform", "position"))
    key, formula = driver(session, target, "value * m", value=0.2, path=ref)
    session.wait(5)
    assert session.command("property.get", reference=ref)["value"] == pytest.approx((0.2,) * 3)
    session.command(
        "driver.formula.update", driver=key, formula=formula, changes={"expression": "value * rad"}
    )
    session.wait(5)
    assert result(session, formula).status == "failed"
    assert session.command("property.get", reference=ref)["value"] == pytest.approx((0.2,) * 3)


def test_actual_geometry_to_formula_cycle_is_detected(session):
    target = curve(session)
    ref = reference(target, ("transform", "position"), 0)
    _, formula = driver(
        session,
        target,
        "x + m",
        path=ref,
        inputs=[dict(name="x", property=reference(target, ("world_transform", "position"), 0))],
    )
    session.wait(5)
    assert result(session, formula).status == "failed"
    assert "Cyclic" in result(session, formula).error


def test_formula_changes_do_not_create_extra_undo_entries(session):
    target = curve(session)
    key, formula = driver(session, target, "value", value=8, kind="INTEGER")
    session.wait(5)
    session.command("driver.value", driver=key, value=11)
    session.wait(5)
    session.command("undo")
    session.wait(5)
    assert session.document.object(target).resolution == 8
    session.command("redo")
    session.wait(5)
    assert session.document.object(target).resolution == 11
    assert result(session, formula).status == "ready"


def test_manual_input_uses_last_accepted_value_and_records_pending(session):
    a, b = curve(session, "A"), curve(session, "B")
    session.command("update_mode", entity=a, mode="MANUAL")
    key, first = driver(session, a, "value", value=8, kind="INTEGER")
    _, second = driver(session, b, "x", inputs=[dict(name="x", property=reference(a))])
    session.wait(5)
    assert session.document.object(b).resolution == 24
    assert first in result(session, second).pending
    session.command("evaluate", entities=[a])
    session.wait(5)
    assert session.document.object(a).resolution == session.document.object(b).resolution == 8
    assert not result(session, second).pending


def test_worker_capture_is_immutable_and_cancellable(session):
    target = curve(session)
    _, formula = driver(session, target, "12")
    context = formula_inputs.Captured(
        session.document, session.resources.snapshot(), session.engine
    )
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(RuntimeError, match="cancelled"):
        formula_evaluation.evaluate(context, {formula}, cancel)
