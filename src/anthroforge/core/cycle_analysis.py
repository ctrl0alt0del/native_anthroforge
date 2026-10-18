"""Iterative strongly connected components of authored output relationships."""

from collections.abc import Mapping, Set

from .results import Port

Edges = Mapping[Port, Set[Port]]


def finish_order(edges: Edges) -> list[Port]:
    seen: set[Port] = set()
    result: list[Port] = []
    for root in edges:
        pending = [(root, False)]
        while pending:
            node, exiting = pending.pop()
            if exiting:
                result.append(node)
            elif node not in seen:
                seen.add(node)
                pending.append((node, True))
                pending.extend((child, False) for child in edges.get(node, ()))
    return result


def collect(edges: Edges, root: Port, remaining: set[Port]) -> frozenset[Port]:
    found, pending = set(), [root]
    while pending:
        node = pending.pop()
        if node in remaining:
            remaining.remove(node)
            found.add(node)
            pending.extend(edges.get(node, ()))
    return frozenset(found)


def cycles(edges: Edges, consumers: Edges) -> tuple[frozenset[Port], ...]:
    remaining, result = set(edges), []
    for root in reversed(finish_order(edges)):
        if root not in remaining:
            continue
        component = collect(consumers, root, remaining)
        if len(component) > 1 or root in edges[root]:
            result.append(component)
    return tuple(result)
