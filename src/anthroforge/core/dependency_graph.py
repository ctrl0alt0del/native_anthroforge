"""Immutable output relationships and reusable reverse/cycle indexes."""

from collections import deque
from collections.abc import Iterator, Mapping, Set
from dataclasses import dataclass
from types import MappingProxyType

from .construction import Control, Deformer
from .entities import SCP
from .results import Port

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

    def __getitem__(self, key: Port) -> frozenset[Port]:
        return self.inputs[key]

    def __len__(self) -> int:
        return len(self.inputs)

    def __iter__(self) -> Iterator[Port]:
        return iter(self.inputs)


def binding_inputs(bindings: tuple[Deformer, ...]) -> set[Port]:
    return {
        Port(b.control, "cage" if b.kind == "LATTICE" else "control") for b in bindings if b.enabled
    }


def parent_inputs(item: SCP, enabled: bool) -> set[Port]:
    if not item.parent or not enabled:
        return set()
    result = {Port(item.parent, "pose")}
    if item.attachment.parent_mode == "SURFACE_NEAREST":
        result.add(Port(item.parent, "geometry"))
    return result


def control_inputs(item: Control, controls: set[str]) -> set[Port]:
    if item.support:
        if item.support in controls:
            return {Port(item.support, "control")}
        inputs = {Port(item.support, "pose")}
        if item.attachment.parent_mode == "SURFACE_NEAREST":
            inputs.add(Port(item.support, "geometry"))
        return inputs
    return {Port(item.follow, "pose")} if item.follow else set()


def entity_edges(entities: tuple[SCP, ...], enabled: bool) -> dict[Port, set[Port]]:
    result: dict[Port, set[Port]] = {}
    for entity in entities:
        pose, geometry = Port(entity.id, "pose"), Port(entity.id, "geometry")
        result[pose] = parent_inputs(entity, enabled)
        inputs = binding_inputs(entity.deformers)
        result[geometry] = inputs | ({pose} if inputs else set())
    return result


def build(
    entities: tuple[SCP, ...], controls: tuple[Control, ...], enabled: bool
) -> DependencyGraph:
    result = entity_edges(entities, enabled)
    control_ids = {c.id for c in controls}
    for control in controls:
        result[Port(control.id, "control")] = control_inputs(control, control_ids)
        result[Port(control.id, "cage")] = {Port(control.id, "control")} | binding_inputs(
            control.deformers
        )
    consumers = reverse(result)
    return DependencyGraph(frozen(result), frozen(consumers), unresolved(result, consumers))
