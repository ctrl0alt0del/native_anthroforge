"""Output-specific dependencies. Pose-following is distinct from geometry feedback."""

from collections import deque

from anthroforge.core.construction import Deformer
from anthroforge.core.document import Document
from anthroforge.core.jobs import Job
from anthroforge.core.results import Port as Port


def graph(document: Document) -> dict[Port, set[Port]]:
    result: dict[Port, set[Port]] = {}
    for entity in document.entities:
        pose, geometry = Port(entity.id, "pose"), Port(entity.id, "geometry")
        result[pose] = parent_inputs(document, entity.id)
        inputs = binding_inputs(entity.deformers)
        result[geometry] = inputs | ({pose} if inputs else set())
    for control in document.controls:
        result[Port(control.id, "control")] = control_inputs(document, control.id)
        result[Port(control.id, "cage")] = {Port(control.id, "control")} | binding_inputs(
            control.deformers
        )
    return result


def parent_inputs(document: Document, entity: str) -> set[Port]:
    item = document.entity(entity)
    if not item.parent or not document.attachments_enabled:
        return set()
    result = {Port(item.parent, "pose")}
    if item.attachment.parent_mode == "SURFACE_NEAREST":
        result.add(Port(item.parent, "geometry"))
    return result


def binding_inputs(bindings: tuple[Deformer, ...]) -> set[Port]:
    return {
        Port(b.control, "cage" if b.kind == "LATTICE" else "control") for b in bindings if b.enabled
    }


def control_inputs(document: Document, control: str) -> set[Port]:
    item = document.control(control)
    if item.support:
        if any(c.id == item.support for c in document.controls):
            return {Port(item.support, "control")}
        inputs = {Port(item.support, "pose")}
        if item.attachment.parent_mode == "SURFACE_NEAREST":
            inputs.add(Port(item.support, "geometry"))
        return inputs
    return {Port(item.follow, "pose")} if item.follow else set()


def reverse(graph: dict[Port, set[Port]]) -> dict[Port, set[Port]]:
    result: dict[Port, set[Port]] = {node: set() for node in graph}
    for node, inputs in graph.items():
        for source in inputs:
            result.setdefault(source, set()).add(node)
    return result


def closure(graph: dict[Port, set[Port]], seeds: set[Port]) -> set[Port]:
    found, queue = set(seeds), deque(seeds)
    while queue:
        for node in graph.get(queue.popleft(), ()):
            if node not in found:
                found.add(node)
                queue.append(node)
    return found


def blocked(graph: dict[Port, set[Port]]) -> set[Port]:
    remaining = {node: len(inputs) for node, inputs in graph.items()}
    consumers = reverse(graph)
    ready = deque(node for node, count in remaining.items() if not count)
    while ready:
        node = ready.popleft()
        del remaining[node]
        for consumer in consumers[node]:
            remaining[consumer] -= 1
            if not remaining[consumer]:
                ready.append(consumer)
    return set(remaining)


def affected(document: Document, seeds: set[Port]) -> set[str]:
    outputs = closure(reverse(graph(document)), seeds)
    return {p.owner for p in outputs if p.output == "geometry"}


def reads(document: Document, entity: str) -> set[str]:
    return {p.owner for p in ports(document, Port(entity, "geometry"))}


def ports(document: Document, output: Port) -> set[Port]:
    return closure(graph(document), {output})


def contract(job: Job, document: Document, outputs: set[Port]) -> None:
    dependencies = graph(document)
    job.provides = frozenset(outputs)
    inputs = closure(dependencies, outputs) - outputs
    job.observes = frozenset(inputs)
    job.prerequisites = frozenset() if outputs & blocked(dependencies) else frozenset(inputs)
