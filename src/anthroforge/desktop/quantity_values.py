"""Exact integer text and display-unit conversion at the Qt command boundary."""

from decimal import Decimal, InvalidOperation, localcontext
from math import pi

from PySide6.QtCore import QObject, Slot

from anthroforge.core.numeric_properties import validate_number
from anthroforge.core.units import factor

INTEGER_FIELDS = {"integer_text", "dimension", "display_units"}


def scale(dimension, units):
    if dimension == "SCALAR":
        return Decimal(1)
    if dimension == "LENGTH":
        return Decimal(str(factor(units)))
    if dimension == "ANGLE":
        return Decimal(str(pi)) / 180
    raise ValueError("Unknown numerical dimension.")


def display_integer(value, dimension, units):
    with localcontext() as context:
        context.prec = 80
        value = Decimal(value) / scale(dimension, units)
        return format(value, ".4f" if dimension == "ANGLE" else ".0f")


def integer_value(text, dimension, units):
    try:
        with localcontext() as context:
            context.prec = 80
            displayed = Decimal(text.replace(",", "."))
            return canonical_integer(displayed, dimension, units)
    except (InvalidOperation, OverflowError):
        raise ValueError("Integer input must be finite numerical text.") from None


def canonical_integer(displayed, dimension, units):
    if not displayed.is_finite():
        raise ValueError("Integer input must be finite.")
    canonical = displayed * scale(dimension, units)
    nearest = canonical.to_integral_value()
    if canonical != nearest:
        if dimension != "ANGLE" or displayed != Decimal(display_integer(nearest, dimension, units)):
            raise ValueError("Integer quantities require a whole value in canonical units.")
    result = int(nearest)
    validate_number(result, "INTEGER")
    return result


def decode(value):
    return integer_value(value["integer_text"], value["dimension"], value["display_units"])


def texts(values, kind):
    return [str(value) for value in values] if kind == "INTEGER" else values


class QuantityValues(QObject):
    @Slot(str, str, str, result=str)
    def displayInteger(self, value, dimension, units):
        return display_integer(value, dimension, units)

    @Slot(str, int, str, str, result=str)
    def offsetInteger(self, value, steps, dimension, units):
        canonical = integer_value(value, dimension, units)
        return display_integer(canonical + steps, dimension, units)
