"""Compile calibrated migration formulas with the application's typed language."""

from skeleton_shortcut_controls import formula, reference
from skeleton_shortcut_hooks import value

from anthroforge.core.expressions import Symbol
from anthroforge.native import expressions


def inputs(mappings, names):
    return [dict(name=name, driver=mappings[source]["driver"]) for name, source in names.items()]


def evaluate(session, expression, incoming):
    symbols, values = [], {}
    drivers = {d.id: d for d in session.document.driving_shortcuts}
    for entry in incoming:
        if "driver" in entry:
            row = drivers[entry["driver"]]
            kind, dimension, current = row.numeric_type, row.dimension, row.value
        else:
            row = session.command("property.get", reference=entry["property"])
            kind, dimension, current = row["numeric_type"], row["dimension"], row["value"]
        symbols.append(Symbol(entry["name"], kind, dimension))
        values[entry["name"]] = current
    return expressions.compile(session.engine, expression, tuple(symbols)).evaluate(values)


def calibrated(session, mapping, ref, expression, incoming, unit=""):
    current, initial = value(session, ref), evaluate(session, expression, incoming)
    factor = "*" + unit if unit else ""
    text = f"{current!r}{factor}+(({expression})-({initial!r}{factor}))"
    formula(session, mapping, ref, text, incoming)


def scaled_frame(session, target, mapping, ratios, incoming):
    for axis, ratio in enumerate(ratios):
        ref = reference(target, "transform", "scale", component=axis)
        calibrated(session, mapping, ref, f"{value(session, ref)!r}*({ratio})", incoming)


def consume_transforms(session, curve):
    for entity in tuple(session.document.entities):
        if entity.primitive and any(use.curve == curve for use in entity.primitive.curves):
            session.command(
                "primitive.curve_mode", entity=entity.id, curve=curve, mode="SHAPE_AND_TRANSFORM"
            )
