"""Automatic routing relationships, independent of viewport and numerical queries."""

from dataclasses import replace
from typing import Any

from . import anatomical_surfaces
from .construction import Curve
from .curve_dependencies import references as explicit_references
from .curve_engines import RoutingSettings
from .cycle_analysis import cycles
from .results import Port


def automatic(item: Any) -> bool:
    return (
        isinstance(item, Curve)
        and isinstance(item.engine_settings, RoutingSettings)
        and (item.engine_settings.obstacle_mode == "AUTO")
    )


def candidates(entities: Any, objects: Any, item: Curve) -> set[Any]:
    assert isinstance(item.engine_settings, RoutingSettings)
    excluded = set(item.engine_settings.excluded_obstacles)
    return {r for r in anatomical_surfaces.defaults(entities, objects) if r.target not in excluded}


def expanded(edges: Any, entities: Any, objects: Any) -> dict[str, frozenset[str]]:
    from .dependency_graph import reverse

    added = {}
    for item in objects:
        if isinstance(item, Curve) and item.engine == "ROUTED":
            edges[Port(item.id, "routing_scope")] = set()
        if automatic(item):
            added[item.id] = candidates(entities, objects, item) - explicit_references(
                item, objects
            )
            edges[Port(item.id, "path")].update(surface_ports(added[item.id]))
    components = cycles(edges, reverse(edges))
    return remove_cyclic_candidates(edges, added, components)


def surface_ports(targets: Any) -> set[Port]:
    return {anatomical_surfaces.port(r) for r in targets} | {
        Port(r.target, "pose") for r in targets
    }


def remove_cyclic_candidates(edges: Any, added: Any, components: Any) -> dict[str, frozenset[str]]:
    rejected = {}
    for key, targets in added.items():
        path = Port(key, "path")
        component: frozenset[Port] = next((c for c in components if path in c), frozenset())
        removed = {t for t in targets if surface_ports({t}) & component}
        rejected[key] = frozenset(t.target for t in removed)
        edges[path].difference_update(surface_ports(removed))
    return rejected


def graph(document: Any, item: Curve) -> Any:
    original = document.registry.construction.get(item.id)
    if original is not None and signature(original) == signature(item):
        return document.index.structure.dependencies
    objects = tuple(item if o.id == item.id else o for o in document.objects)
    if original is None:
        objects = (*objects, item)
    return replace(document, objects=objects).index.structure.dependencies


def signature(item: Any) -> Any:
    if not isinstance(item, Curve):
        return None
    settings = item.engine_settings
    return (
        item.parent,
        tuple(sorted(explicit_references(item))),
        (
            (settings.obstacle_mode, settings.excluded_obstacles)
            if isinstance(settings, RoutingSettings)
            else None
        ),
        tuple(p.junction for p in item.points),
    )


def targets(document: Any, item: Curve) -> tuple[str, ...]:
    return membership(graph(document, item), item.id)


def references(document: Any, item: Curve) -> tuple[Any, ...]:
    return tuple(
        sorted(
            anatomical_surfaces.from_port(p)
            for p in graph(document, item).get(Port(item.id, "path"), ())
            if p.output in ("geometry", "base", "final")
        )
    )


def membership(graph: Any, key: str) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                p.owner
                for p in graph.get(Port(key, "path"), ())
                if p.output in ("geometry", "base", "final")
            }
        )
    )


def scene_signature(edges: Any, entities: Any, objects: Any = ()) -> tuple[str, ...]:
    needed = surface_ports(anatomical_surfaces.defaults(entities, objects))
    pending = list(needed)
    while pending:
        for port in edges.get(pending.pop(), ()):
            if port not in needed:
                needed.add(port)
                pending.append(port)
    return tuple(sorted(edge_token(port, edges) for port in needed))


def edge_token(port: Port, edges: Any) -> str:
    values = sorted((p.owner, p.output) for p in edges.get(port, ()))
    return repr((port.owner, port.output, values))
