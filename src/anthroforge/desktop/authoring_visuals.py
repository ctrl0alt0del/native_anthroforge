"""Component categories stay distinguishable through hover and selection."""


def category(reference):
    part = reference["part"]
    return "points" if part == "position" else "handles" if part in ("left", "right") else "other"


def layers(editor):
    result = {name: [] for name in ("points", "handles", "other")}
    for ref, world, _ in editor.rows:
        result[category(ref)].append(world)
    result["curves"] = [p for path in editor._curve_lines.values() for p in path]
    result["links"] = editor._lines[len(result["curves"]) :]
    return result


def highlights(editor):
    from .authoring_state import component_key

    result = {name: [] for name in ("points", "handles", "other")}
    for index, (ref, world, _) in enumerate(editor.rows):
        if component_key(ref) in editor.selection or index == editor.hover_index:
            result[category(ref)].append(world)
    return result
