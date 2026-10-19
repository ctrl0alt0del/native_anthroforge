"""Atomic final bundles remove entity-level cycles without removing source dependencies."""

from collections.abc import Mapping

from .cycle_analysis import cycles
from .objects import ObjectRecord
from .results import Port
from .tissues import TissueVCP


def groups(records: Mapping[str, ObjectRecord]) -> dict[str, frozenset[str]]:
    edges = relationships(records)
    consumers: dict[Port, set[Port]] = {node: set() for node in edges}
    for node, inputs in edges.items():
        for parent in inputs:
            consumers[parent].add(node)
    return {
        p.owner: frozenset(q.owner for q in group)
        for group in cycles(edges, consumers)
        for p in group
    }


def relationships(records: Mapping[str, ObjectRecord]) -> dict[Port, set[Port]]:
    edges = {
        Port(item.id, "final"): {Port(p, "final") for p in item.stack_plan.providers}
        for item in records.values()
        if isinstance(item, TissueVCP) and item.stacking
    }
    for inputs in tuple(edges.values()):
        for parent in inputs:
            edges.setdefault(parent, set())
    return edges


def members(records: Mapping[str, ObjectRecord], target: str) -> frozenset[str]:
    return groups(records).get(target, frozenset((target,)))


def inputs(records: Mapping[str, ObjectRecord], group: frozenset[str]) -> set[Port]:
    plans = {Port(key, "plan") for key in group}
    providers = {parent for key in group for parent in providers_of(records[key])}
    return plans | {Port(key, "final") for key in providers - group}


def providers_of(item: ObjectRecord) -> tuple[str, ...]:
    return item.stack_plan.providers if isinstance(item, TissueVCP) and item.stacking else ()
