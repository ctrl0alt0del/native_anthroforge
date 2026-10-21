"""Batch pose outputs without contracting intervening geometry into a wait cycle."""

from collections import defaultdict
from graphlib import TopologicalSorter

from anthroforge.core.document import Document
from anthroforge.core.results import Port

from . import dependencies


def groups(document: Document, targets: set[str]) -> list[set[str]]:
    graph = dependencies.graph(document)
    outputs = {Port(key, "pose") for key in targets}
    valid = {key: value for key, value in graph.items() if key not in graph.blocked}
    levels: dict[Port, int] = {}
    for port in TopologicalSorter(valid).static_order():
        levels[port] = max(
            (levels[p] + int(port in outputs and p not in outputs) for p in valid[port]),
            default=0,
        )
    batches: dict[int, set[str]] = defaultdict(set)
    for port in outputs:
        batches[levels.get(port, -1)].add(port.owner)
    return [batches[level] for level in sorted(batches)] or [set()]
