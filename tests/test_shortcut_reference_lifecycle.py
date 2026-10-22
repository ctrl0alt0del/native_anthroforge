"""Stable property addresses and generated-path dependencies through public operations."""

import numpy as np
import pytest

from anthroforge.core.formula_dependencies import property_port, property_reference
from anthroforge.core.numeric_properties import PropertyRef
from tests.test_driving_formulas import curve, driver, reference, result
from tests.test_parametric_curves import circle_settings, create, positions


@pytest.mark.parametrize("name", ["left/right:weight", "100%", "radius α", "@part#0"])
def test_property_ports_preserve_named_members_and_components(name):
    original = PropertyRef("tissue", ("fields", "@" + name, "values"), 2)
    assert property_reference(property_port(original)) == original


@pytest.mark.parametrize("enabled", [True, False])
def test_lattice_input_address_blocks_resizing_until_formula_removed(session, enabled):
    cage = session.command("control.create", kind="LATTICE")
    target = curve(session)
    point = reference(cage, ("points", "#1"), 0)
    key, formula = driver(session, target, "8", inputs=[dict(name="x", property=point)])
    session.command(
        "driver.formula.update", driver=key, formula=formula, changes=dict(enabled=enabled)
    )
    before = session.document.control(cage)
    with pytest.raises(ValueError, match="references.*resizing"):
        session.command("property.set", reference=reference(cage, ("resolution",), 0), value=3)
    assert session.document.control(cage) == before
    session.command("driver.formula.remove", driver=key, formula=formula)
    session.command("property.set", reference=reference(cage, ("resolution",), 0), value=3)
    assert session.document.control(cage).resolution == (3, 2, 2)


def feedback_driver(session, target):
    item = session.document.object(target)
    variable = reference(
        target,
        ("engine_settings", "variables", "@" + item.engine_settings.variables[0].id, "value"),
    )
    point = reference(target, ("points", "@" + item.points[0].id, "position"), 0)
    return driver(session, target, "x", path=variable, inputs=[dict(name="x", property=point)])


def test_generated_coordinate_feedback_retains_path_and_unrelated_formula_runs(session):
    target = create(session, **circle_settings())
    before = positions(session, target)
    _, feedback = feedback_driver(session, target)
    other = curve(session)
    _, independent = driver(session, other, "9")
    session.wait(5)
    assert result(session, feedback).status == "failed"
    assert "Cyclic" in result(session, feedback).error
    assert result(session, independent).status == "ready"
    assert session.document.object(other).resolution == 9
    np.testing.assert_array_equal(positions(session, target), before)


def rename_radius(session, target, variable):
    session.command(
        "curve.parametric.variable.update",
        curve=target,
        variable=variable,
        changes=dict(name="radius"),
    )
    session.command(
        "curve.parametric.configure",
        curve=target,
        changes=dict(x="radius*cos(t)", y="radius*sin(t)"),
    )
    session.wait(5)


def test_variable_rename_retains_property_identity_and_referenced_removal_is_rejected(session):
    target = create(session, **circle_settings())
    variable = session.document.object(target).engine_settings.variables[0].id
    ref = reference(target, ("engine_settings", "variables", "@" + variable, "value"))
    other = curve(session)
    driver(session, other, "round(x/m)+8", inputs=[dict(name="x", property=ref)])
    rename_radius(session, target, variable)
    assert session.command("property.get", reference=ref)["value"] == 0.3
    with pytest.raises(ValueError, match="Resolve driving shortcut"):
        session.command("curve.parametric.variable.remove", curve=target, variable=variable)
