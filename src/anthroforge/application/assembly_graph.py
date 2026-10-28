"""One copy inventory: selected records, nested identities and explicit boundary references."""

import json
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from anthroforge.core import graph_records, object_registry
from anthroforge.core.entities import SCP
from anthroforge.core.numeric_properties import PropertyRef


@dataclass(frozen=True)
class Boundary:
    key: str
    source: str
    name: str
    kind: str
    relationship: str
    role: str
    uses: tuple[tuple[str, graph_records.Reference], ...]
    property: PropertyRef | None = None


def roots(selection: Any) -> tuple[str, ...]:
    return tuple(
        k
        for k, v in selection.records.items()
        if isinstance(v, SCP) and v.parent not in selection.records
    )


def records(selection: Any) -> tuple[Any, ...]:
    return (*selection.records.values(), *selection.junctions, *selection.drivers)


def identities(selection: Any, resources: Any = None) -> dict[str, str]:
    values = records(selection)
    if resources:
        values += tuple(p.authored for p in resources.paths.values())
    owned = set().union(*(graph_records.owned(value) for value in values))
    return {key: str(uuid4()) for key in owned}


def owned(selection: Any) -> set[str]:
    return set().union(*(graph_records.owned(value) for value in records(selection)))


def boundaries(document: Any, selection: Any) -> tuple[Boundary, ...]:
    internal = owned(selection)
    grouped: dict[str, list[Any]] = {}
    sources = {}
    for item in records(selection):
        for ref in graph_records.references(item):
            if ref.target in internal or hierarchy_boundary(item, ref):
                continue
            key, prop = boundary_key(item, ref)
            grouped.setdefault(key, []).append((item.id, ref))
            sources[key] = (ref, prop)
    return tuple(boundary(document, key, sources[key], uses) for key, uses in grouped.items())


def hierarchy_boundary(item: Any, ref: graph_records.Reference) -> bool:
    return isinstance(item, SCP) and ref.path == ("parent",)


def at(value: Any, path: tuple[str | int, ...]) -> Any:
    for token in path:
        value = value[token] if isinstance(token, int) else getattr(value, token)
    return value


def boundary_key(item: Any, ref: graph_records.Reference) -> tuple[str, PropertyRef | None]:
    container = at(item, ref.path[:-1])
    prop = container if isinstance(container, PropertyRef) else None
    address = (prop.path, prop.component) if prop else ()
    return json.dumps((ref.target, ref.relationship, ref.role, address)), prop


def boundary(document: Any, key: str, source: Any, uses: Any) -> Boundary:
    ref, prop = source
    item = document.registry.records.get(ref.target)
    if item is not None:
        name, kind = item.name, object_registry.kind(item)
    else:
        declared = next((v for v in document.external_references if v.id == ref.target), None)
        name, kind = (declared.name, declared.kind) if declared else (ref.target, "REFERENCE")
    return Boundary(key, ref.target, name, kind, ref.relationship, ref.role, tuple(uses), prop)


def included_decisions(mappings: dict[str, Any], boundaries: tuple[Boundary, ...]) -> set[str]:
    return {row.source for row in boundaries if decision(mappings, row).get("action") == "include"}


def decision(mappings: dict[str, Any], row: Boundary) -> dict[str, Any]:
    value = mappings.get(row.key, mappings.get(row.source, {}))
    return dict(value) if isinstance(value, dict) else dict(action="map", target=value)
