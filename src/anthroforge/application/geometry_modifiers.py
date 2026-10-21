"""Ordered geometry stages share deformer lifecycle, topology and transaction policies."""

from dataclasses import replace
from typing import Any

from anthroforge.core.construction import Deformer, Target

from . import deformer_operations as bindings
from .construction_policy import require_topology_edit


def validate_change(document: Any, owner: Any, values: Any) -> None:
    def topology(rows: Any) -> tuple[Any, ...]:
        return tuple((b.id, b.subdivision) for b in rows if b.kind == "SUBDIVISION" and b.enabled)

    if topology(owner.deformers) != topology(values):
        require_topology_edit(document, owner.id)


def settings(kind: str, options: dict[str, Any]) -> dict[str, Any]:
    if kind == "SUBDIVISION" and not set(options) - {"levels"}:
        return dict(subdivision=options.get("levels", 1))
    if kind == "DISPLACE" and not set(options) - {"offset"}:
        return dict(displacement=tuple(options.get("offset", (0, 0, 0))))
    raise ValueError("Choose Simple Subdivision levels or local displacement offset.")


def add(session: Any, entity: str, kind: str, **options: Any) -> str:
    target = Target(entity)
    bindings.validate_target(session, target, kind)
    binding = Deformer(kind, "", target, **settings(kind, options))
    bindings.install(session, target, (*bindings.owner(session, target).deformers, binding))
    return binding.id


def update(session: Any, binding: str, **options: Any) -> None:
    current = bindings.locate(session, binding)
    changed = replace(current, **settings(current.kind, options))
    values = tuple(
        changed if b.id == binding else b for b in bindings.owner(session, current.target).deformers
    )
    bindings.install(session, current.target, values)
