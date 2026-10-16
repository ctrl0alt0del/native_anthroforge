"""Authored changes invalidate only the output ports whose inputs actually changed."""

from dataclasses import replace

from anthroforge.core.entities import SCP
from anthroforge.core.results import Port

GEOMETRY_FIELDS = ("primitive", "deformers", "thickness")
POSE_FIELDS = ("matrix", "geometry_offset", "parent", "attachment")


def differs(previous: SCP, current: SCP, fields: tuple[str, ...]) -> bool:
    return any(getattr(previous, name) != getattr(current, name) for name in fields)


def changed_ports(previous: SCP, current: SCP) -> set[Port]:
    fields = {"pose": POSE_FIELDS, "geometry": GEOMETRY_FIELDS}
    return {
        Port(current.id, kind)
        for kind, names in fields.items()
        if differs(previous, current, names)
    }


def authored(previous: SCP, current: SCP) -> SCP:
    return replace(
        current,
        generation=previous.generation + 1,
        construction_revision=previous.construction_revision
        + int(differs(previous, current, GEOMETRY_FIELDS)),
    )
