"""Reviewed graph replacement with precise read validation and isolated resource ownership."""

from dataclasses import dataclass, field, replace
from typing import Any

from anthroforge.core.jobs import ObsoleteInputs
from anthroforge.core.results import Port
from anthroforge.core.skeleton_update import BoneChange, Finding

from . import dependencies, skeleton_graph
from .assembly_candidate import ReadSet, readset

GROUPS = (
    "entities",
    "objects",
    "controls",
    "junctions",
    "shortcuts",
    "driving_shortcuts",
    "formula_results",
    "imports",
    "external_references",
)


@dataclass(frozen=True)
class Reads:
    records: ReadSet
    relationships: tuple[tuple[Port, frozenset[Port], frozenset[Port]], ...]
    attachments_enabled: bool

    def require(self, document: Any) -> None:
        self.records.require(document)
        graph = dependencies.graph(document)
        if document.attachments_enabled != self.attachments_enabled:
            raise ObsoleteInputs("Attachment evaluation settings changed; prepare again.")
        for port, inputs, consumers in self.relationships:
            if (
                graph.get(port, frozenset()) != inputs
                or graph.consumers.get(port, frozenset()) != consumers
            ):
                raise ObsoleteInputs("An affected relationship changed; prepare again.")


@dataclass(frozen=True)
class Candidate:
    baseline: Any
    document: Any
    resources: Any
    reads: Reads
    identities: dict[str, str]
    changes: tuple[BoneChange, ...]
    findings: tuple[Finding, ...]
    prepared: frozenset[Port]
    evidence: tuple[dict[str, Any], ...] = ()
    comparison: dict[str, Any] = field(default_factory=dict)
    skin: dict[str, Any] = field(default_factory=dict)

    @property
    def ready(self) -> bool:
        return not any(row.blocking for row in self.findings)

    def merge(self, current: Any) -> Any:
        self.reads.require(current)
        updates = {
            name: skeleton_graph.merge_records(getattr(current, name), rows)
            for name, rows in self.changed().items()
        }
        if self.document.skin != self.baseline.skin:
            updates["skin"] = self.document.skin
        return replace(current, **updates)

    def changed(self) -> dict[str, tuple[Any, ...]]:
        return {
            name: changed_records(getattr(self.baseline, name), getattr(self.document, name))
            for name in GROUPS
        }


def changed_records(before: Any, after: Any) -> tuple[Any, ...]:
    records = {skeleton_graph.identity(item): item for item in before}
    return tuple(item for item in after if records.get(skeleton_graph.identity(item)) != item)


def reads(context: Any, seeds: set[Port], extra: set[str]) -> Reads:
    graph = dependencies.graph(context.document)
    affected = dependencies.closure(dependencies.reverse(graph), seeds)
    required = dependencies.closure(graph, affected)
    keys = ({p.owner for p in required} | extra) & context.baseline.registry.records.keys()
    original = dependencies.graph(context.baseline)
    relationships = tuple(
        (p, original.get(p, frozenset()), original.consumers.get(p, frozenset()))
        for p in affected
        if p in original
    )
    return Reads(
        readset(context.baseline, keys), relationships, context.baseline.attachments_enabled
    )
