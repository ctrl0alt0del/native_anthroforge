"""Component categories stay distinguishable through hover and selection."""

from . import presentation


def category(reference):
    part = reference["part"]
    if part == "field":
        weight = reference["weight"]
        return "fieldLow" if weight <= 0 else "fieldHigh" if weight >= 1 else "fieldMid"
    return "points" if part == "position" else "handles" if part in ("left", "right") else "other"


LAYERS = ("points", "handles", "other", "fieldLow", "fieldMid", "fieldHigh")


def layers(editor):
    result = {name: [] for name in LAYERS}
    for ref, world, _ in editor.rows:
        if presentation.component(editor, ref):
            result[category(ref)].append(world)
    curves = [p for path in editor._curve_lines.values() for p in path]
    result["curves"] = curves if presentation.allows(editor, "curves") else []
    category_name = link_category(editor)
    result["links"] = (
        editor._lines[len(curves) :] if presentation.allows(editor, category_name) else []
    )
    return result


def link_category(editor):
    owner = editor.controller
    control = owner.session.document.index.controls.get(owner.selection)
    return "cages" if control and control.kind == "LATTICE" else "handles"


def highlights(editor):
    from .authoring_state import component_key

    result = {name: [] for name in LAYERS}
    for index, (ref, world, _) in enumerate(editor.rows):
        active = component_key(ref) in editor.selection or index == editor.hover_index
        if active and presentation.component(editor, ref):
            result[category(ref)].append(world)
    return result
