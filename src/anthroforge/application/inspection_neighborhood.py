"""Read-only relationship neighborhoods; no workspace or scheduling modifications."""

from typing import Any

from anthroforge.core.mirroring import source

from .dependencies import closure


def describe(session: Any, target: str) -> dict[str, Any]:
    document = session.document
    if source(target) not in document.registry.records:
        raise ValueError("Select anatomy or construction to inspect its neighborhood.")
    graph = document.index.structure.dependencies
    seeds = {p for p in graph if p.owner in (target, source(target))}
    upstream = {p.owner for p in closure(graph, seeds)}
    members = {target, source(target)} | upstream
    members.update(attached_children(document, source(target)))
    return result(document, target, members)


def result(document: Any, target: str, members: set[str]) -> dict[str, Any]:
    known = document.registry.records.keys() | document.mirrors.instances.keys()
    return dict(
        target=target,
        members=sorted(members & known),
        revision=document.revision,
        explanation="Selection, upstream sources and supports, and direct attachment children.",
    )


def attached_children(document: Any, target: str) -> set[str]:
    result = {e.id for e in document.entities if e.parent == target}
    for item in document.objects:
        bindings = getattr(item, "bindings", ())
        binding = getattr(item, "binding", None)
        if any(b.target == target for b in bindings) or (
            binding and binding.reference.target == target
        ):
            result.add(item.id)
    return result
