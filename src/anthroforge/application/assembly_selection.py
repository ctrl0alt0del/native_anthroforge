"""Import closure distinguishes required construction from external anatomical support."""

from dataclasses import dataclass
from typing import Any

from anthroforge.core import graph_records, junctions
from anthroforge.core.entities import descendants
from anthroforge.core.fibers import Fiber
from anthroforge.core.mirroring import source as original
from anthroforge.core.tissues import TissueVCP


@dataclass(frozen=True)
class Selection:
    records: dict[str, Any]
    reasons: dict[str, str]
    junctions: tuple[Any, ...]
    drivers: tuple[Any, ...]
    shortcuts: tuple[Any, ...] = ()


def expand(document: Any, selected: list[str], attached: bool = False) -> Selection:
    records = document.registry.records
    seeds = {original(key) for key in selected}
    if not seeds or seeds - records.keys():
        raise ValueError("Select existing anatomy or construction to import.")
    reasons = {key: "Selected" for key in seeds}
    for key in tuple(seeds & document.index.entities.keys()):
        reasons.update({v: "SCP subtree" for v in descendants(document.entities, key) - seeds})
    if attached:
        reasons.update({key: "Attached tissue" for key in attached_tissues(document, set(reasons))})
    complete_sources(document, reasons)
    picked = {key: records[key] for key in reasons}
    shared = selected_junctions(document, picked)
    return selection_records(document, picked, reasons, shared)


def selection_records(document: Any, picked: Any, reasons: Any, shared: Any) -> Selection:
    wrappers = tuple(s for s in document.shortcuts if s.reference.target in picked)
    return Selection(picked, reasons, shared, selected_drivers(document, set(picked)), wrappers)


def complete_sources(document: Any, reasons: dict[str, str]) -> None:
    pending = list(reasons)
    groups = junctions.members(document.objects)
    while pending:
        key = pending.pop()
        item = document.object(key)
        required = {r.target for r in graph_records.references(item) if r.required}
        for target in required:
            additions = {ref.curve for ref in groups[target]} if target in groups else {target}
            for source in additions - reasons.keys():
                document.object(source)
                reasons[source] = "Required by " + item.name
                pending.append(source)


def selected_junctions(document: Any, records: dict[str, Any]) -> tuple[Any, ...]:
    shared = {r.target for item in records.values() for r in graph_records.references(item)}
    return tuple(row for row in document.junctions if row.id in shared)


def attached_tissues(document: Any, selected: set[str]) -> set[str]:
    supports = {
        v.id: tissue_supports(document, v.source, set())
        for v in document.objects
        if isinstance(v, TissueVCP)
    }
    found = set(selected)
    while added := {key for key, targets in supports.items() if targets & found} - found:
        found |= added
    return found - selected


def tissue_supports(document: Any, key: str, visited: set[str]) -> set[str]:
    if key in visited:
        return set()
    visited.add(key)
    item = document.registry.records.get(key)
    if isinstance(item, Fiber):
        return {binding.target for binding in item.bindings}
    if isinstance(item, TissueVCP):
        return tissue_supports(document, item.source, visited)
    result = {item.binding.reference.target} if hasattr(item, "binding") else set()
    for use in getattr(item, "curves", ()):
        result |= tissue_supports(document, use.curve, visited)
    return result


def selected_drivers(document: Any, selected: set[str]) -> tuple[Any, ...]:
    found = {
        d.id
        for d in document.driving_shortcuts
        if any(f.target.target in selected for f in d.formulas)
    }
    pending, index = list(found), {d.id: d for d in document.driving_shortcuts}
    while pending:
        driver = index[pending.pop()]
        for formula in driver.formulas:
            for entry in formula.inputs:
                if entry.driver in index and entry.driver not in found:
                    found.add(entry.driver)
                    pending.append(entry.driver)
    return tuple(d for d in document.driving_shortcuts if d.id in found)
