"""Named output relationships and precise cycle evidence for every client."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.dependency_graph import DependencyGraph
from anthroforge.core.document import Document
from anthroforge.core.results import Port

from .dependencies import closure


def port_records(document: Document, ports: set[Port] | frozenset[Port]) -> list[dict[str, Any]]:
    return [port_record(document, p) for p in sorted(ports, key=lambda p: (p.owner, p.output))]


def port_record(document: Document, port: Port) -> dict[str, Any]:
    item = document.index.entities.get(port.owner) or document.index.controls.get(port.owner)
    return dict(asdict(port), name=item.name if item else "Unavailable object")


def cycle_context(graph: DependencyGraph, port: Port) -> dict[str, Any]:
    if port not in graph.blocked:
        return dict(participant=False, components=(), own=frozenset())
    reachable = closure(graph, {port})
    causes = tuple(group for group in graph.cycles if group & reachable)
    own = next((group for group in causes if port in group), frozenset())
    return dict(participant=bool(own), components=causes, own=own)


def cycle_records(document: Document, port: Port) -> dict[str, Any]:
    graph = document.index.structure.dependencies
    context = cycle_context(graph, port)
    return dict(
        participant=context["participant"],
        member_component=port_records(document, context["own"]),
        blocked=port in graph.blocked,
        cycles=[port_records(document, group) for group in context["components"]],
    )


def relationships(document: Document, owner: str) -> list[dict[str, Any]]:
    graph = document.index.structure.dependencies
    return [
        dict(
            output=p.output,
            inputs=port_records(document, graph[p]),
            consumers=port_records(document, graph.consumers[p]),
            **cycle_records(document, p),
        )
        for p in graph
        if p.owner == owner
    ]
