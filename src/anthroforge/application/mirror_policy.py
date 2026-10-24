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
    return (*parent_references(value), *relationship_references(value))


def relationship_references(value: Any) -> tuple[SurfaceReference, ...]:
    return tuple(
        ref
        for name in RELATIONSHIPS
        if hasattr(value, name)
        for ref in references(getattr(value, name))
    )


def parent_references(value: Any) -> tuple[SurfaceReference, ...]:
    rule = getattr(getattr(value, "attachment", None), "parent_instance", "")
    return (SurfaceReference(value.parent, instance=rule),) if rule and value.parent else ()


def blockers(document: Any, removed: set[str]) -> list[dict[str, str]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    for item in document.registry.records.values():
        add_stacking_blockers(rows, item, removed)
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


def add_stacking_blockers(rows: Any, item: Any, removed: set[str]) -> None:
    plan = getattr(getattr(item, "stack_plan", None), "providers", ())
    intent = tuple(r.other for r in getattr(item, "stack_relationships", ()))
    for target in set(plan) | set(intent):
        if target in removed:
            rows[item.id, target] = dict(
                id=item.id, name=item.name, instance=target, reason="Stacking provider reference"
            )


def require_transition(before: Any, after: Any) -> None:
    removed = before.mirrors.instances.keys() - after.mirrors.instances.keys()
    affected = (
        [row for row in blockers(before, removed) if row["id"] in after.registry.records]
        if removed
        else []
    )
    if affected:
        names = ", ".join(row["name"] for row in affected)
        raise ValueError("Mirror removal is blocked by referenced consumers: " + names)


def removing(document: Any, target: str) -> list[dict[str, str]]:
    removed = {
        v.id for v in document.mirrors.instances.values() if v.source == target or v.rule == target
    }
    rows = blockers(document, removed)
    rows.extend(
        dict(id=o.id, name=o.name, reason="Symmetric construction plane", instance="")
        for o in document.objects
        if getattr(getattr(o, "symmetric", None), "rule", "") == target
        or getattr(getattr(o, "mirror_plane", None), "rule", "") == target
    )
    return [r for r in rows if r["id"] != target]


def require_removal(document: Any, target: str) -> None:
    rows = removing(document, target)
    if rows:
        raise ValueError(
            "Mirror removal is blocked by referenced consumers: "
            + ", ".join(row["name"] for row in rows)
        )
