"""Transform properties expose canonical metres/radians through native TRS adapters."""

from collections.abc import Iterator
from dataclasses import replace
from math import degrees, radians
from typing import Any

from anthroforge.core.numeric_properties import NumericDescriptor, PropertyRef

from .object_frames import Frames
from .transform_policy import object_reason, require_object_transform

GROUPS = {"position": (0, "LENGTH"), "rotation": (3, "ANGLE"), "scale": (6, "SCALAR")}


def descriptors(item: Any) -> Iterator[NumericDescriptor]:
    reason = object_reason(item)
    for scope in ("transform", "world_transform"):
        for group, (_, dimension) in GROUPS.items():
            writable = scope == "transform" and not reason
            yield NumericDescriptor(
                PropertyRef(item.id, (scope, group)),
                scope.replace("_", " ").title() + " " + group,
                "REAL",
                dimension,
                3,
                writable,
                reason if scope == "transform" else "Evaluated input only",
                vector=True,
            )


def read(session: Any, reference: PropertyRef, item: Any = None) -> Any:
    item = item or session.document.object(reference.target)
    matrix = item.matrix
    if reference.path[0] == "world_transform":
        matrix = Frames(session.engine, session.document).world(item.id)
    index, _ = GROUPS[reference.path[1]]
    values = tuple(session.engine.decompose(matrix)[index : index + 3])
    if index == 3:
        values = tuple(radians(v) for v in values)
    return values if reference.component is None else values[reference.component]


def changed(session: Any, item: Any, updates: Any) -> Any:
    require_object_transform(item)
    values = list(session.engine.decompose(item.matrix))
    for reference, replacement in updates:
        if reference.path[0] != "transform":
            raise ValueError("Evaluated world transforms are read-only formula inputs.")
        index, _ = GROUPS[reference.path[1]]
        components = range(3) if reference.component is None else (reference.component,)
        replacements = replacement if reference.component is None else (replacement,)
        for component, value in zip(components, replacements, strict=True):
            values[index + component] = degrees(value) if index == 3 else value
    return replace(item, matrix=session.engine.transform(values))
