"""Variable identity survives symbol edits without breaking the curve's expressions."""

import numpy as np
import pytest

from anthroforge.core.expressions import RESERVED, Symbol
from anthroforge.native import expressions
from tests.test_parametric_curves import circle_settings, create, positions


def renamed(session, curve, name):
    variable = session.document.object(curve).engine_settings.variables[0].id
    session.command(
        "curve.parametric.variable.update", curve=curve, variable=variable, changes=dict(name=name)
    )
    session.wait(5)
    return session.document.object(curve)


def test_rename_keeps_equations_geometry_and_one_undo_action(session):
    curve = create(session, **circle_settings())
    before, cursor = positions(session, curve), session.history.cursor
    updated = renamed(session, curve, "radius")
    assert updated.result.status == "ready"
    assert updated.engine_settings.x == "radius*cos(t)"
    assert updated.engine_settings.y == "radius*sin(t)"
    np.testing.assert_array_equal(positions(session, curve), before)
    assert session.history.cursor == cursor + 1
    session.command("undo")
    session.wait(5)
    assert session.document.object(curve).engine_settings.variables[0].name == "r"
    np.testing.assert_array_equal(positions(session, curve), before)


def test_rename_updates_interval_expressions_without_substring_replacement(session):
    curve = create(
        session,
        x="r*t*m",
        y="radius*m",
        z="floor(r)*m",
        interval=dict(start_expression="r-1", end_expression="r+radius"),
        variables=[dict(name="r", value=1.0), dict(name="radius", value=2.0)],
    )
    updated = renamed(session, curve, "width").engine_settings
    assert (updated.x, updated.y, updated.z) == ("width*t*m", "radius*m", "floor(width)*m")
    assert updated.interval.start_expression == "width-1"
    assert updated.interval.end_expression == "width+radius"


def test_referenced_symbol_cannot_be_removed_without_resolving_equations(session):
    curve = create(session, **circle_settings())
    before = session.document
    variable = before.object(curve).engine_settings.variables[0].id
    with pytest.raises(ValueError, match="expression"):
        session.command("curve.parametric.variable.remove", curve=curve, variable=variable)
    assert session.document == before


@pytest.mark.parametrize("name", ["sin", "round", "pi", "t"])
def test_reserved_symbol_rename_is_rejected_before_mutating_document(session, name):
    curve = create(session, **circle_settings())
    before = session.document
    with pytest.raises(ValueError, match="reserved"):
        renamed(session, curve, name)
    assert session.document == before


def test_atomic_symbol_swap_preserves_variable_identities_and_equations(session):
    from dataclasses import asdict

    curve = create(
        session, x="a*t*m", y="b*m", variables=[dict(name="a"), dict(name="b", value=2.0)]
    )
    before = positions(session, curve)
    variables = [asdict(v) for v in session.document.object(curve).engine_settings.variables]
    variables[0]["name"], variables[1]["name"] = "b", "a"
    session.command("curve.parametric.configure", curve=curve, changes=dict(variables=variables))
    session.wait(5)
    config = session.document.object(curve).engine_settings
    assert (config.x, config.y) == ("b*t*m", "a*m")
    np.testing.assert_array_equal(positions(session, curve), before)


def test_unused_variable_removal_and_explicit_equation_replacement(session):
    curve = create(session, **circle_settings())
    session.command(
        "curve.parametric.configure", curve=curve, changes=dict(x="t*m", y="0", variables=[])
    )
    session.wait(5)
    assert session.document.object(curve).result.status == "ready"
    unused = session.command("curve.parametric.variable.add", curve=curve, name="unused")
    session.command("curve.parametric.variable.remove", curve=curve, variable=unused)
    session.wait(5)
    assert not session.document.object(curve).engine_settings.variables


@pytest.mark.parametrize("name", sorted(RESERVED))
def test_core_reserved_names_match_native_language(session, name):
    symbol = object.__new__(Symbol)
    for field, value in (("name", name), ("numeric_type", "REAL"), ("dimension", "SCALAR")):
        object.__setattr__(symbol, field, value)
    with pytest.raises(ValueError, match="reserved"):
        expressions.compile(session.engine, "0", (symbol,))
