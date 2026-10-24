"""Session-owned reverse read index for conservative formula-change candidates."""

from collections import defaultdict
from typing import Any

from anthroforge.core.results import Port

from . import dependencies


def changed_keys(before: Any, after: Any) -> set[str]:
    if before is after:
        return set()
    return {key for key in before.keys() | after.keys() if before.get(key) is not after.get(key)}


def owners_changed(before: Any, after: Any) -> set[str]:
    return set().union(
        changed_keys(before.registry.records, after.registry.records),
        changed_keys(before.formula_index.drivers, after.formula_index.drivers),
        changed_keys(before.formula_index.results, after.formula_index.results),
    )


class FormulaInvalidation:
    def __init__(self) -> None:
        self.graph: Any = None
        self.readers: dict[str, set[str]] = {}

    def index(self, document: Any) -> None:
        graph = dependencies.graph(document)
        if self.graph is graph:
            return
        readers: dict[str, set[str]] = defaultdict(set)
        for key in document.formula_index.formulas:
            inputs = dependencies.ports(document, Port(key, "formula")) - {Port(key, "formula")}
            for port in inputs:
                readers[port.owner].add(key)
        self.graph, self.readers = graph, dict(readers)

    def candidates(self, before: Any, after: Any) -> set[str]:
        if dependencies.graph(before) is not dependencies.graph(after):
            return set(after.formula_index.formulas)
        self.index(after)
        changed = changed_keys(before.formula_index.formulas, after.formula_index.formulas)
        for owner in owners_changed(before, after):
            changed.update(self.readers.get(owner, ()))
        return changed.intersection(after.formula_index.formulas)
