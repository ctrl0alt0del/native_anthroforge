"""All incident half-path seams constrain one shared world point before atomic expansion."""

from typing import Any

from anthroforge.native.components import constrained_axes

from .symmetric_paths import plane


def project(session: Any, references: Any, world: Any) -> Any:
    values: dict[str, float] = {}
    for ref in references:
        item = session.document.object(ref.curve)
        if item.symmetric and ref.point in (item.points[0].id, item.points[-1].id):
            rule = plane(session.document, item.symmetric)
            if rule.axis in values and values[rule.axis] != rule.shift:
                raise ValueError("The shared seam inherits incompatible parallel planes.")
            values[rule.axis] = rule.shift
    return constrained_axes(session.engine, [world], values)[0].tolist() if values else world
