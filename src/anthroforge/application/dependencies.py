"""Application traversal and job contracts over snapshot-owned dependency indexes."""

from collections import deque
from collections.abc import Mapping, Set

from anthroforge.core import dependency_graph as index
from anthroforge.core.document import Document
from anthroforge.core.jobs import Job
from anthroforge.core.results import Port as Port


def graph(document: Document) -> index.DependencyGraph:
    return document.index.structure.dependencies


def reverse(graph: index.Edges) -> index.Edges:
    return graph.consumers if isinstance(graph, index.DependencyGraph) else index.reverse(graph)


def closure[T](graph: Mapping[T, Set[T]], seeds: Set[T]) -> set[T]:
    found, queue = set(seeds), deque(seeds)
    while queue:
        for node in graph.get(queue.popleft(), ()):
            if node not in found:
                found.add(node)
                queue.append(node)
    return found


def frontier[T](graph: Mapping[T, Set[T]], seeds: Set[T], barriers: Set[T]) -> set[T]:
    """Stop publication fan-out at outputs that must evaluate before notifying consumers."""
    found, seen, queue = set(), set(seeds), deque(seeds)
    while queue:
        for node in graph.get(queue.popleft(), ()):
            if node in seen:
                continue
            seen.add(node)
            if node in barriers:
                found.add(node)
            else:
                queue.append(node)
    return found


def blocked(graph: index.Edges) -> frozenset[Port]:
    return (
        graph.blocked
        if isinstance(graph, index.DependencyGraph)
        else index.unresolved(graph, reverse(graph))
    )


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
