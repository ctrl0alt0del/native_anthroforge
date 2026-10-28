"""Hierarchical topology reservations; metadata policy, not numerical density solving."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Any


def explicit(document: Any) -> dict[str, Any]:
    return {
        s.owner: s
        for s in document.skin.contributors
        if s.density_mode == "SUBTREE_BUDGET" and s.owner in document.index.entities
    }


def parent(document: Any, owner: str, rules: Any) -> str:
    seen = {owner}
    current = document.index.entities[owner].parent
    while current and current not in seen:
        if current in rules:
            return str(current)
        seen.add(current)
        current = document.index.entities[current].parent
    return ""


def children(document: Any, rules: Any) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    for owner in rules:
        result[parent(document, owner, rules)].append(owner)
    return result


def errors(document: Any) -> tuple[str, ...]:
    rules = explicit(document)
    nested, result = children(document, rules), []
    for owner, descendants in nested.items():
        reserved = sum(rules[key].target_quads for key in descendants)
        budget = (
            rules[owner].target_quads if owner else document.skin.topology_settings.target_quads
        )
        if reserved > budget:
            label = document.object(owner).name if owner else "Document"
            result.append(f"{label}: child budgets {reserved} exceed {budget} target quads.")
    return tuple(result)


@dataclass(frozen=True)
class Region:
    owner: str
    requested: int
    exclusive: int


@dataclass(frozen=True)
class Plan:
    owners: tuple[str, ...]
    owner_regions: tuple[int, ...]
    regions: tuple[Region, ...]


def region_records(document: Any, rules: Any) -> tuple[Region, ...]:
    nested, result = children(document, rules), []
    for owner in (*sorted(rules), ""):
        requested = (
            rules[owner].target_quads if owner else document.skin.topology_settings.target_quads
        )
        reserved = sum(rules[key].target_quads for key in nested.get(owner, ()))
        result.append(Region(owner, requested, requested - reserved))
    return tuple(result)


def plan(document: Any) -> Plan:
    problems = errors(document)
    if problems:
        raise ValueError(" ".join(problems))
    rules = explicit(document)
    regions = region_records(document, rules)
    indices = {row.owner: index for index, row in enumerate(regions)}
    owners = tuple(sorted(document.index.entities))
    mapped = tuple(indices[key if key in rules else parent(document, key, rules)] for key in owners)
    return Plan(owners, mapped, regions)
