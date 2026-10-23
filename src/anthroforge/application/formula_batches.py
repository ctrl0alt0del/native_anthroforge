"""Batch expressions only across paths the expression evaluator can resolve itself."""

from collections import deque
from typing import Any

from anthroforge.core.results import Port

from . import dependencies, formula_candidates, formula_inputs


def predecessors(graph: Any, key: str, selected: set[str]) -> dict[str, int]:
    found: dict[str, int] = {}
    seen, queue = set(), deque((p, False) for p in graph[Port(key, "formula")])
    while queue:
        port, barrier = queue.popleft()
        if (port, barrier) in seen or port in graph.blocked:
            continue
        seen.add((port, barrier))
        if port.output == "formula":
            if port.owner in selected:
                found[port.owner] = max(found.get(port.owner, 0), int(barrier))
        else:
            external = port.output != "driver" and not port.output.startswith("property:")
            queue.extend((p, barrier or external) for p in graph.get(port, ()))
    return found


def coherent_groups(document: Any, ids: set[str]) -> list[set[str]]:
    records = formula_inputs.formulas(document)
    groups: dict[Any, set[str]] = {}
    for key in ids:
        identity = formula_candidates.group(document, records[key][1].target)
        groups.setdefault(identity, set()).add(key)
    return list(groups.values())


def ranks(document: Any, ids: set[str]) -> tuple[dict[str, int], set[str]]:
    graph = dependencies.graph(document)
    edges = {key: predecessors(graph, key, ids) for key in ids}
    levels, groups, changed = dict.fromkeys(ids, 0), coherent_groups(document, ids), set()
    for _ in range(len(ids) + 1):
        before = levels.copy()
        for key, inputs in edges.items():
            levels[key] = max((levels[p] + cost for p, cost in inputs.items()), default=0)
        for group in groups:
            value = max(levels[key] for key in group)
            levels.update((key, value) for key in group)
        changed = {key for key in ids if levels[key] != before[key]}
        if not changed:
            break
    return levels, changed


def plan(document: Any, ids: set[str]) -> list[set[str]]:
    levels, invalid = ranks(document, ids)
    groups: dict[int, set[str]] = {}
    for key, level in levels.items():
        groups.setdefault(-1 if key in invalid else level, set()).add(key)
    return [groups[level] for level in sorted(groups)]


def failures(document: Any, ids: set[str]) -> dict[str, str]:
    _, invalid = ranks(document, ids)
    return {
        key: "Coupled property formulas require mutually dependent evaluated outputs."
        for key in invalid
    }
