"""Prepare reference repair from the destination's retained evidence, without its source file."""

from dataclasses import dataclass, replace
from types import SimpleNamespace
from typing import Any

from anthroforge.core import graph_records

from . import (
    assembly_bindings,
    assembly_graph,
    assembly_metadata,
    assembly_provenance,
    assembly_result_state,
)
from .assembly_candidate import ReadSet, readset
from .assembly_mapping import Mappings
from .resources import Resources


@dataclass(frozen=True)
class Repair:
    additions: dict[str, tuple[Any, ...]]
    resources: Resources
    references: tuple[Any, ...]
    reads: ReadSet
    findings: tuple[Any, ...] = ()
    evidence: tuple[Any, ...] = ()
    mappings: tuple[Any, ...] = ()
    selection: Any = None
    identities: Any = None

    @property
    def ready(self) -> bool:
        return not any(row.get("blocking") for row in self.findings)

    def merge(self, document: Any) -> Any:
        self.reads.require(document)
        changes = {}
        for group, rows in self.additions.items():
            updated = {identity(item): item for item in rows}
            changes[group] = tuple(
                updated.get(identity(item), item) for item in getattr(document, group)
            )
        mapped = {r.id: r for r in self.references}
        changes["external_references"] = tuple(
            mapped.get(r.id, r) for r in document.external_references
        )
        return replace(document, **changes)


class Preparation:
    def __init__(self, engine: Any, payload: Any, choices: Any, cancel: Any) -> None:
        self.engine, self.cancel = engine, cancel
        self.destination, self.available = payload
        self.source = SimpleNamespace(document=self.destination)
        self.loaded, self.resources = self.available.snapshot(), Resources()
        self.options: dict[str, Any] = {}
        self.assets: dict[str, str] = {}
        self.evidence: tuple[dict[str, Any], ...] = ()
        self.values, rows = affected(self.destination, choices)
        self.ids = {item.id: item.id for values in self.values.values() for item in values}
        self.mapping = Mappings(self.source, self.destination, self.ids, choices)
        self.mapping.assess(rows)
        self.mapping.references = restored_references(self.destination, self.mapping.references)

    def run(self) -> Repair:
        for group, rows in self.values.items():
            self.values[group] = tuple(
                self.mapping.patch(item, assembly_provenance.restore(self.destination, item))
                for item in rows
            )
        assembly_metadata.repair(self)
        if self.candidate().ready:
            self.evidence = assembly_bindings.assess(self, self.candidate())
            self.include_dependents()
            assembly_provenance.rewrite(self)
            assembly_result_state.mark(self)
        return self.candidate()

    def include_dependents(self) -> None:
        document = self.candidate().merge(self.destination)
        changed = {v.id for rows in self.values.values() for v in rows}
        affected = assembly_result_state.changed_outputs(document, changed)
        owners = {p.owner for p in affected}
        for group in ("entities", "objects", "controls"):
            previous = {v.id for v in self.values[group]}
            self.values[group] += tuple(
                assembly_provenance.restore(self.destination, v)
                for v in getattr(document, group)
                if v.id in owners - previous
            )

    def candidate(self) -> Repair:
        keys = self.mapping.reads | {identity(v) for rows in self.values.values() for v in rows}
        keys |= {"external:" + r.id for r in self.mapping.references}
        return Repair(
            self.values,
            self.resources,
            tuple(self.mapping.references),
            readset(self.destination, keys),
            tuple(self.mapping.findings),
            self.evidence,
            tuple(self.mapping.rows),
            {},
            self.ids,
        )


def record(document: Any, key: str) -> Any:
    return next(
        (d for d in document.driving_shortcuts if d.id == key), document.registry.records.get(key)
    )


def identity(item: Any) -> str:
    return str(getattr(item, "id", getattr(item, "formula", "")))


def affected(document: Any, choices: Any) -> tuple[Any, Any]:
    missing = {r.id for r in document.external_references if not r.target}
    if set(choices) - missing:
        raise ValueError("Resolve only current unresolved import reference identities.")
    selected = referring_records(document, set(choices))
    selection = SimpleNamespace(
        records={},
        junctions=(),
        shortcuts=(),
        drivers=tuple(v for rows in selected.values() for v in rows),
    )
    boundaries = tuple(
        r for r in assembly_graph.boundaries(document, selection) if r.source in choices
    )
    return selected, boundaries


def referring_records(document: Any, targets: set[str]) -> dict[str, Any]:
    groups = ("entities", "objects", "controls", "driving_shortcuts", "shortcuts")
    return {
        k: tuple(
            v
            for v in getattr(document, k)
            if any(r.target in targets for r in graph_records.references(v))
        )
        for k in groups
    }


def restored_references(document: Any, references: Any) -> list[Any]:
    originals = {r.id: r for r in document.external_references}
    return [
        replace(originals[r.source_entity], target=r.target, instance=r.instance)
        for r in references
    ]


def prepare(engine: Any, choices: Any, payload: Any, cancel: Any) -> Repair:
    return Preparation(engine, payload, choices, cancel).run()
