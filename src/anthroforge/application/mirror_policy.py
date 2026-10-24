"""Shared removal safety and retained anatomical references for spatial instances."""

from dataclasses import is_dataclass
from typing import Any

from anthroforge.core.mirroring import MirrorInstance, require_source
from anthroforge.core.surface_references import SurfaceReference

RELATIONSHIPS = (
    "binding",
    "bindings",
    "supports",
    "constraints",
    "deformers",
    "shrinkwrap",
    "surface",
    "reference",
    "engine_settings",
    "obstacles",
    "targets",
)


def require_edit(arguments: dict[str, Any]) -> None:
    for key in ("entity", "target", "curve", "control", "source"):
        value = arguments.get(key)
        if isinstance(value, str):
            require_source(value)


def retain_settings(document: Any, changes: dict[str, Any]) -> dict[str, Any]:
    if not document.mirror_rules or not {"entities", "controls", "objects"} & changes.keys():
        return changes
    live = {
        v.id
        for group in ("entities", "controls", "objects")
        for v in changes.get(group, getattr(document, group))
    }
    rules = tuple(r for r in changes.get("mirror_rules", document.mirror_rules) if r.target in live)
    shared = tuple(r for r in document.shared_mirror_targets if r.source in live)
    return dict(changes, mirror_rules=rules, shared_mirror_targets=shared)


def references(value: Any) -> tuple[SurfaceReference, ...]:
    if isinstance(value, SurfaceReference):
        return (value,)
    if isinstance(value, (tuple, list)):
        return tuple(ref for item in value for ref in references(item))
    if not is_dataclass(value):
        return ()
    return tuple(
        ref
        for name in RELATIONSHIPS
        if hasattr(value, name)
        for ref in references(getattr(value, name))
    )


def blockers(document: Any, removed: set[str]) -> list[dict[str, str]]:
    rows = {}
    for item in document.registry.records.values():
        for ref in references(item):
            identity = MirrorInstance(ref.target, ref.instance).id if ref.instance else ""
            if identity in removed:
                rows[(item.id, identity)] = dict(
                    id=item.id,
                    name=item.name,
                    instance=identity,
                    reason="Retained surface reference",
                )
    return list(rows.values())


def require_transition(before: Any, after: Any) -> None:
    removed = before.mirrors.instances.keys() - after.mirrors.instances.keys()
    affected = blockers(after, removed) if removed else []
    if affected:
        names = ", ".join(row["name"] for row in affected)
        raise ValueError("Mirror removal is blocked by referenced consumers: " + names)
