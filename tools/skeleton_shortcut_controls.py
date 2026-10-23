"""Explicit source-to-property mappings that preserve existing authored construction."""

DIRECT = {
    "SHORTCUT_3": ("scale", 2),
    "SHORTCUT_15": ("scale", 0),
    "SHORTCUT_16": ("scale", 0),
    "SHORTCUT_17": ("scale", 2),
    "SHORTCUT_98": ("scale", 2),
    "SHORTCUT_99": ("scale", 2),
    "SHORTCUT_103": ("scale", None),
    "SHORTCUT_104": ("position", 1),
}


def reference(target, *path, component=None):
    return dict(target=target, path=list(path), component=component)


def expose_simple(session, shortcuts):
    result = []
    for row in shortcuts:
        if row["id"] in DIRECT:
            field, component = DIRECT[row["id"]]
            ref = reference(row["owner_id"], "transform", field, component=component)
            value = session.command("property.get", reference=ref)["value"]
            key = session.command("shortcut.expose", reference=ref, label=row["name"])
            result.append(dict(source=row["id"], wrapper=key, reference=ref, value=value))
    return result


def driver(session, row, dimension):
    value = row["resolved"]["captured"]["value"]
    key = session.command("driver.create", label=row["name"], value=value, dimension=dimension)
    return dict(source=row["id"], driver=key, value=value, formulas=[])


def formula(session, mapping, ref, expression, inputs=None):
    key = session.command(
        "driver.formula.add",
        driver=mapping["driver"],
        target=ref,
        expression=expression,
        inputs=inputs,
    )
    mapping["formulas"].append(dict(formula=key, target=ref, expression=expression))


def angle_formula(session, mapping, use, field, sign):
    ref = reference("SCP_2", "primitive", "curves", "@" + use.id, field)
    initial = session.command("property.get", reference=ref)["value"]
    expression = (
        f"{initial!r} + (value - {mapping['value']!r}*rad)*{sign!r}/(6.2829999923706055*rad)"
    )
    formula(session, mapping, ref, expression)


def expose_rib_angles(session, shortcuts):
    result = []
    rows = {row["id"]: row for row in shortcuts}
    uses = session.document.entity("SCP_2").primitive.curves
    for source, selected in (("SHORTCUT_2", uses[1:]), ("SHORTCUT_9", uses[:1])):
        mapping = driver(session, rows[source], "ANGLE")
        for use in selected:
            angle_formula(session, mapping, use, "span", 1.0)
            angle_formula(session, mapping, use, "start", -0.5)
        result.append(mapping)
    return result
