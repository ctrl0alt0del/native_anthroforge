"""Shared removal safety and retained anatomical references for spatial instances."""

from dataclasses import is_dataclass
from typing import Any

from anthroforge.core.mirroring import MirrorInstance
from anthroforge.core.surface_references import SurfaceReference

RELATIONSHIPS = (
    "binding", "bindings", "supports", "constraints", "deformers", "shrinkwrap",
    "surface", "reference", "engine_settings", "obstacles", "targets",
)


def references(value: Any) -> tuple[SurfaceReference, ...]:
    if isinstance(value, SurfaceReference):
        return (value,)
    if isinstance(value, (tuple, list)):
        return tuple(ref for item in value for ref in references(item))
    if not is_dataclass(value):
        return ()
    return tuple(
        ref for name in RELATIONSHIPS if hasattr(value, name)
        for ref in references(getattr(value, name))
    )


def blockers(document: Any, removed: set[str]) -> list[dict[str, str]]:
    rows = {}
    for item in document.registry.records.values():
        for ref in references(item):
            identity = MirrorInstance(ref.target, ref.instance).id if ref.instance else ""
            if identity in removed:
                rows[(item.id, identity)] = dict(
                    id=item.id, name=item.name, instance=identity, reason="Retained surface reference"
                )
    return list(rows.values())


def require_transition(before: Any, after: Any) -> None:
    removed = before.mirrors.instances.keys() - after.mirrors.instances.keys()
    affected = blockers(after, removed) if removed else []
    if affected:
        names = ", ".join(row["name"] for row in affected)
        raise ValueError("Mirror removal is blocked by referenced consumers: " + names)
