"""Immutable output relationships and reusable reverse/cycle indexes."""

from collections import deque
from collections.abc import Iterator, Mapping, Set
from dataclasses import dataclass, field
from types import MappingProxyType

from . import deformer_references, junctions, routing_obstacles, tissue_dependencies
from .construction import Control, Curve, Deformer
from .curve_dependencies import inputs as curve_path_inputs
from .cycle_analysis import cycles
from .entities import SCP
from .object_outputs import output
from .objects import ObjectRecord
from .results import Port
from .surfaces import Surface

Edges = Mapping[Port, Set[Port]]


def reverse(edges: Edges) -> dict[Port, set[Port]]:
    result: dict[Port, set[Port]] = {node: set() for node in edges}
    for node, inputs in edges.items():
        for source in inputs:
            result.setdefault(source, set()).add(node)
    return result


def unresolved(edges: Edges, consumers: Edges) -> frozenset[Port]:
    remaining = {node: len(inputs) for node, inputs in edges.items()}
    ready = deque(node for node, count in remaining.items() if not count)
    while ready:
        node = ready.popleft()
        del remaining[node]
        for consumer in consumers[node]:
            remaining[consumer] -= 1
            if not remaining[consumer]:
                ready.append(consumer)
    return frozenset(remaining)


def frozen(edges: Edges) -> Mapping[Port, frozenset[Port]]:
    return MappingProxyType({key: frozenset(value) for key, value in edges.items()})


@dataclass(frozen=True, slots=True)
class DependencyGraph(Mapping[Port, frozenset[Port]]):
    inputs: Mapping[Port, frozenset[Port]]
    consumers: Mapping[Port, frozenset[Port]]
    blocked: frozenset[Port]
    cycles: tuple[frozenset[Port], ...] = ()
    routing_excluded: Mapping[str, frozenset[str]] = field(default_factory=dict)
    routing_scene: tuple[str, ...] = ()

    def __getitem__(self, key: Port) -> frozenset[Port]:
        return self.inputs[key]

    def __len__(self) -> int:
        return len(self.inputs)

    def __iter__(self) -> Iterator[Port]:
        return iter(self.inputs)


def binding_inputs(bindings: tuple[Deformer, ...]) -> set[Port]:
    return set().union(*(deformer_references.inputs(b) for b in bindings))


def parent_inputs(item: SCP, enabled: bool) -> set[Port]:
    if not item.parent or not enabled:
        return set()
    result = {Port(item.parent, "pose")}
    if item.attachment.parent_mode == "SURFACE_NEAREST":
        result.add(Port(item.parent, "geometry"))
    return result


def control_inputs(item: Control) -> set[Port]:
    return {Port(item.follow, "pose")} if item.follow else set()


def entity_edges(
    entities: tuple[SCP, ...], enabled: bool, objects: tuple[ObjectRecord, ...] = ()
) -> dict[Port, set[Port]]:
    result: dict[Port, set[Port]] = {}
    for entity in entities:
        pose, geometry = Port(entity.id, "pose"), Port(entity.id, "geometry")
        result[pose] = parent_inputs(entity, enabled)
        inputs = binding_inputs(entity.deformers)
        result[geometry] = inputs | ({pose} if inputs else set())
        if entity.primitive:
            for use in entity.primitive.curves:
                result[geometry] |= curve_inputs(use, objects)
    return result


def build(
    entities: tuple[SCP, ...],
    controls: tuple[Control, ...],
    enabled: bool,
    objects: tuple[ObjectRecord, ...] = (),
    shared: tuple[junctions.Junction, ...] = (),
) -> DependencyGraph:
    result = entity_edges(entities, enabled, objects)
    result.update(object_edges(objects, shared))
    result.update(tissue_dependencies.edges(objects))
    result.update(junctions.edges(shared))
    result.update(control_edges(controls))
    signature = routing_obstacles.scene_signature(result, entities, objects)
    excluded = routing_obstacles.expanded(result, entities, objects)
    return indexed(result, excluded, signature)


def mirror_edges(edges: dict[Port, set[Port]]) -> dict[Port, set[Port]]:
    owners = {p.owner for p in edges}
    return {
        ref: set()
        for values in edges.values()
        for ref in values
        if ref.output == "mirror" and ref.owner in owners
    }


def control_edges(controls: tuple[Control, ...]) -> dict[Port, set[Port]]:
    result = {}
    for control in controls:
        result[Port(control.id, "control")] = control_inputs(control)
        result[Port(control.id, "pose")] = {Port(control.id, "control")}
        result[Port(control.id, "cage")] = {Port(control.id, "control")} | binding_inputs(
            control.deformers
        )
    return result


def indexed(
    result: dict[Port, set[Port]],
    excluded: dict[str, frozenset[str]] | None = None,
    signature: tuple[str, ...] = (),
) -> DependencyGraph:
    result.update(mirror_edges(result))
    consumers = reverse(result)
    return DependencyGraph(
        frozen(result),
        frozen(consumers),
        unresolved(result, consumers),
        cycles(result, consumers),
        MappingProxyType(excluded or {}),
        signature,
    )


def object_edges(
    objects: tuple[ObjectRecord, ...], shared: tuple[junctions.Junction, ...] = ()
) -> dict[Port, set[Port]]:
    result: dict[Port, set[Port]] = {}
    for item in objects:
        pose = Port(item.id, "pose")
        result[Port(item.id, "local_pose")] = set()
        result[pose] = {Port(item.id, "local_pose")} | (
            {Port(item.parent, "pose")} if item.parent else set()
        )
        result[Port(item.id, output(item))] = construction_inputs(item, objects, shared)
    return result


def construction_inputs(
    item: ObjectRecord,
    objects: tuple[ObjectRecord, ...],
    shared: tuple[junctions.Junction, ...] = (),
) -> set[Port]:
    if isinstance(item, Curve):
        return curve_path_inputs(item, objects) | junctions.inputs(item, shared)
    if isinstance(item, Surface):
        return set().union(*(curve_inputs(use, objects) for use in item.curves))
    return tissue_dependencies.inputs(item, objects)


def curve_inputs(use: object, objects: tuple[ObjectRecord, ...]) -> set[Port]:
    from .curve_uses import CurveUse

    assert isinstance(use, CurveUse)
    result = {Port(use.curve, "path")}
    if use.mode == "SHAPE_ONLY":
        return result
    parents = {item.id: item.parent for item in objects}
    key, seen = use.curve, set()
    while key and key != use.reference_frame and key not in seen:
        result.add(Port(key, "local_pose" if key in parents else "pose"))
        seen.add(key)
        key = parents.get(key, "")
    return result
