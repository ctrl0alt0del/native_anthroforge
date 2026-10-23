"""Typed UI transport preserves native int64 values, units and ordinary edit failures."""

import pytest

from anthroforge.desktop.controller_actions import command_values
from anthroforge.desktop.quantity_values import display_integer, integer_value
from tests.test_tissue_interaction import controller as controller


@pytest.mark.parametrize("value", [-(1 << 63), 9007199254740993, (1 << 63) - 1])
@pytest.mark.parametrize("dimension,units", [("SCALAR", "m"), ("LENGTH", "mm"), ("ANGLE", "m")])
def test_exact_integer_display_roundtrip_across_dimensions(value, dimension, units):
    text = display_integer(str(value), dimension, units)
    assert integer_value(text, dimension, units) == value


@pytest.mark.parametrize("text,dimension", [("1.5", "SCALAR"), ("500", "LENGTH"), ("45", "ANGLE")])
def test_integer_display_rejects_fractional_canonical_quantities(text, dimension):
    with pytest.raises(ValueError, match="whole value"):
        integer_value(text, dimension, "mm")


@pytest.mark.parametrize("text", ["NaN", "Infinity", "-Infinity", "9223372036854775808"])
def test_integer_text_rejects_nonfinite_and_out_of_range_values(text):
    with pytest.raises(ValueError, match="finite|range"):
        integer_value(text, "SCALAR", "m")


def payload(text, dimension="SCALAR", units="m"):
    return dict(integer_text=text, dimension=dimension, display_units=units)


def test_transport_decodes_nested_integer_text_without_changing_strings():
    value = dict(name="9007199254740993", values=[payload("9007199254740993"), 1.5])
    assert command_values(value) == dict(name="9007199254740993", values=[9007199254740993, 1.5])


def test_driver_editor_and_list_preserve_exact_integer_input(controller):
    session, panel = controller.session, controller.shortcut_panel
    key = session.command("driver.create", numeric_type="INTEGER", value=9007199254740993)
    panel.configure(True, True, "")
    panel.editor.select(key)
    assert panel.editor.details["valueText"] == "9007199254740993"
    assert panel.model.rows[0]["values"] == ["9007199254740993"]
    panel.editor.setValue(payload("9007199254740995"))
    assert session.document.driving_shortcuts[0].value == 9007199254740995
    panel.editValue(key, -1, payload("9007199254740997"), False)
    assert session.document.driving_shortcuts[0].value == 9007199254740997


def test_invalid_integer_edit_retains_document_and_history(controller):
    session = controller.session
    key = session.command("driver.create", numeric_type="INTEGER", value=8)
    controller.shortcut_panel.editor.select(key)
    before, cursor = session.document, session.history.cursor
    controller.shortcut_panel.editor.setValue(payload("9223372036854775808"))
    assert session.document is before and session.history.cursor == cursor
    assert "64-bit" in controller.message


@pytest.mark.parametrize("value", [-(1 << 63) - 1, 1 << 63, 10**400])
def test_authored_integer_driver_rejects_values_outside_native_range(session, value):
    with pytest.raises(ValueError, match="64-bit"):
        session.command("driver.create", numeric_type="INTEGER", value=value)


def test_authored_integer_variable_rejects_values_outside_native_range(session):
    curve = session.command("curve.create", engine="PARAMETRIC")
    with pytest.raises(ValueError, match="64-bit"):
        session.command(
            "curve.parametric.variable.add",
            curve=curve,
            name="n",
            numeric_type="INTEGER",
            value=1 << 63,
        )
