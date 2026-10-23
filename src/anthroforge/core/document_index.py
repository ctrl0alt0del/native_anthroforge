"""Snapshot-owned indexes; reuse validated relationships across value-only edits."""

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from . import construction_validation, dependency_graph, formula_dependencies, snapshot_definitions
from .construction import Control
from .deformer_references import signature as binding_signature
from .entities import SCP, validate_tree

if TYPE_CHECKING:
    from .document import Document


def reference_signature(item: SCP | Control) -> tuple[Any, ...]:
    bindings = tuple(binding_signature(b) for b in item.deformers)
    ids = tuple(construction_validation.identities(item))
    if isinstance(item, Control):
        return (ids, bindings, item.kind, item.follow)
    primitive = item.primitive
    targets = primitive_references(primitive) if primitive else None
    return (ids, bindings, item.parent, item.attachment.parent_mode, targets)


def primitive_references(primitive: Any) -> tuple[Any, ...]:
    curves = tuple((c.id, c.mode, c.reference_frame) for c in primitive.curves)
    return curves, tuple(p.id for p in primitive.pieces)


@dataclass(frozen=True, slots=True)
class Structure:
    signatures: Mapping[str, tuple[Any, ...]]
    order: tuple[str, ...]
    children: Mapping[str, tuple[str, ...]]
    depths: Mapping[str, int]
    dependencies: dependency_graph.DependencyGraph
    attachments: bool
    object_links: tuple[Any, ...] = ()


@dataclass(frozen=True, slots=True)
class DocumentIndex:
    source_entities: tuple[SCP, ...]
    source_controls: tuple[Control, ...]
    entities: Mapping[str, SCP]
    controls: Mapping[str, Control]
    structure: Structure
    source_objects: tuple[Any, ...] = ()
    source_junctions: tuple[Any, ...] = ()
    source_drivers: tuple[Any, ...] = ()


def signatures(document: "Document", previous: DocumentIndex | None) -> dict[str, tuple[Any, ...]]:
    result = {}
    items: tuple[SCP | Control, ...] = (*document.entities, *document.controls)
    for item in items:
        old = previous.entities.get(item.id) or previous.controls.get(item.id) if previous else None
        result[item.id] = (
            previous.structure.signatures[item.id]
            if previous and old is item
            else reference_signature(item)
        )
    return result


def tree_layout(
    entities: tuple[SCP, ...],
) -> tuple[tuple[str, ...], Mapping[str, tuple[str, ...]], Mapping[str, int]]:
    children: dict[str, list[str]] = {}
    for item in entities:
        children.setdefault(item.parent, []).append(item.id)
    order, depths = breadth_first(children)
    return order, MappingProxyType({k: tuple(v) for k, v in children.items()}), depths


def breadth_first(children: Mapping[str, list[str]]) -> tuple[tuple[str, ...], Mapping[str, int]]:
    order, depths = [], {}
    pending = deque((key, 0) for key in children.get("", ()))
    while pending:
        key, depth = pending.popleft()
        order.append(key)
        depths[key] = depth
        pending.extend((child, depth + 1) for child in children.get(key, ()))
    return tuple(order), MappingProxyType(depths)


def validated_structure(
    document: "Document", signature: dict[str, tuple[Any, ...]], links: tuple[Any, ...]
) -> Structure:
    validate_tree(document.entities)
    construction_validation.document(document)
    layout = tree_layout(document.entities)
    graph = construction_graph(document)
    return Structure(
        MappingProxyType(signature),
        *layout,
        graph,
        document.attachments_enabled,
        links,
    )


def construction_graph(document: "Document") -> dependency_graph.DependencyGraph:
    graph = dependency_graph.build(
        document.entities,
        document.controls,
        document.attachments_enabled,
        document.objects,
        document.junctions,
    )
    return with_formulas(document, graph)


def with_formulas(
    document: "Document", graph: dependency_graph.DependencyGraph
) -> dependency_graph.DependencyGraph:
    if not document.driving_shortcuts:
        return graph
    edges = {port: set(inputs) for port, inputs in graph.items()}
    records = {v.id: v for v in (*document.entities, *document.controls, *document.objects)}
    formula_dependencies.extend(edges, document.driving_shortcuts, records)
    return dependency_graph.indexed(edges, dict(graph.routing_excluded), graph.routing_scene)


def structure(document: "Document", previous: DocumentIndex | None) -> Structure:
    signature = signatures(document, previous)
    links = object_links(document, previous)
    if previous and previous.structure.attachments == document.attachments_enabled:
        if (
            signature == previous.structure.signatures
            and same_order(document, previous)
            and links == previous.structure.object_links
        ):
            return previous.structure
    return validated_structure(document, signature, links)


def same_order(document: "Document", previous: DocumentIndex) -> bool:
    return tuple(e.id for e in document.entities) == tuple(previous.entities) and tuple(
        c.id for c in document.controls
    ) == tuple(previous.controls)


def record_maps(
    document: "Document", previous: DocumentIndex | None
) -> tuple[Mapping[str, SCP], Mapping[str, Control]]:
    entities = previous.entities if previous else None
    controls = previous.controls if previous else None
    if not previous or document.entities is not previous.source_entities:
        entities = MappingProxyType({e.id: e for e in document.entities})
    if not previous or document.controls is not previous.source_controls:
        controls = MappingProxyType({c.id: c for c in document.controls})
    assert entities is not None and controls is not None
    return entities, controls


def reusable(document: "Document", previous: DocumentIndex) -> bool:
    return (
        document.entities is previous.source_entities
        and document.controls is previous.source_controls
        and document.objects is previous.source_objects
        and document.junctions is previous.source_junctions
        and document.driving_shortcuts is previous.source_drivers
        and document.attachments_enabled == previous.structure.attachments
    )


def build(document: "Document", previous: DocumentIndex | None) -> DocumentIndex:
    if previous and reusable(document, previous):
        return previous
    relationships = structure(document, previous)
    entities, controls = record_maps(document, previous)
    return DocumentIndex(
        document.entities,
        document.controls,
        entities,
        controls,
        relationships,
        document.objects,
        document.junctions,
        document.driving_shortcuts,
    )


def object_links(document: "Document", previous: DocumentIndex | None = None) -> tuple[Any, ...]:
    cached = cached_links(document, previous)
    return (
        tuple(
            cached[o.id][1]
            if o.id in cached and snapshot_definitions.same(cached[o.id][0], o)
            else object_link(o, document)
            for o in document.objects
        )
        + document.junctions
        + formula_dependencies.signature(document.driving_shortcuts)
    )


def link_context(objects: tuple[Any, ...]) -> tuple[Any, ...]:
    # Other records affect source roles, parent-frame walks and junction dependencies.
    return tuple((o.id, type(o), o.parent) for o in objects)


def cached_links(document: "Document", previous: DocumentIndex | None) -> dict[str, Any]:
    if not previous or document.junctions != previous.source_junctions:
        return {}
    if link_context(document.objects) != link_context(previous.source_objects):
        return {}
    return {
        item.id: (item, link)
        for item, link in zip(
            previous.source_objects, previous.structure.object_links, strict=False
        )
    }


def object_link(item: Any, document: "Document") -> tuple[Any, ...]:
    from . import tissue_dependencies
    from .dependency_graph import construction_inputs
    from .routing_obstacles import signature

    return (
        item.id,
        type(item).__name__,
        getattr(item, "engine", ""),
        item.parent,
        frozenset(construction_inputs(item, document.objects, document.junctions)),
        tuple(c.curve for c in getattr(item, "curves", ())),
        signature(item),
        tissue_dependencies.signature(item),
    )
