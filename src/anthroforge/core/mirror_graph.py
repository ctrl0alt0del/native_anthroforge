"""Reflected providers are graph aliases of source outputs, never extra producers."""

from dataclasses import replace
from typing import Any

from . import anatomical_surfaces, dependency_graph, routing_obstacles
from .results import Port
from .surface_references import SurfaceReference


def install(document: Any) -> None:
    index, mirrors = document.index, document.mirrors
    structure = index.structure
    identities = tuple(mirrors.instances)
    if identities == structure.mirror_instances:
        return
    base = structure.mirror_base or structure.dependencies
    graph = reflected_graph(document, base) if identities else base
    structure = replace(structure, dependencies=graph, mirror_base=base if identities else None,
                        mirror_instances=identities)
    object.__setattr__(document, "_index", replace(index, structure=structure))


def references(document: Any) -> tuple[SurfaceReference, ...]:
    return tuple(SurfaceReference(value.source, role, value.rule)
                 for value in document.mirrors.instances.values()
                 if value.source in document.registry.anatomy
                 for role in anatomical_surfaces.roles(document.object(value.source), document.registry.records))


def aliases(ref: SurfaceReference) -> set[Port]:
    source = SurfaceReference(ref.target, ref.role)
    return {anatomical_surfaces.port(source), Port(ref.target, "pose"), Port(ref.instance, "mirror")}


def reflected_graph(document: Any, base: Any) -> Any:
    edges = {key: set(value) for key, value in base.items()}
    refs = references(document)
    edges.update({anatomical_surfaces.port(ref): aliases(ref) for ref in refs})
    edges.update({Port(ref.instance, "mirror"): set() for ref in refs})
    added = automatic_inputs(document, edges, refs)
    components = dependency_graph.cycles(edges, dependency_graph.reverse(edges))
    excluded = routing_obstacles.remove_cyclic_candidates(edges, added, components)
    keys = base.routing_excluded.keys() | excluded.keys()
    exclusions = {key: base.routing_excluded.get(key, frozenset()) | excluded.get(key, frozenset())
                  for key in keys}
    signature = (*base.routing_scene, repr(tuple(document.mirrors.instances)))
    return dependency_graph.indexed(edges, exclusions, signature)


def automatic_inputs(document: Any, edges: Any, refs: Any) -> dict[str, set[SurfaceReference]]:
    added = {}
    for item in document.objects:
        if not routing_obstacles.automatic(item):
            continue
        port = Port(item.id, "path")
        excluded = set(item.engine_settings.excluded_obstacles)
        values = {ref for ref in refs if ref.role != "TISSUE_BASE" and ref.target not in excluded
                  and anatomical_surfaces.port(SurfaceReference(ref.target, ref.role)) in edges[port]}
        added[item.id] = values
        edges[port].update(routing_obstacles.surface_ports(values))
    return added
