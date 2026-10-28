"""Reviewed graph replacement with precise read validation and isolated resource ownership."""

from dataclasses import dataclass, field, replace
from typing import Any

from anthroforge.core.jobs import ObsoleteInputs
from anthroforge.core.results import Port
from anthroforge.core.skeleton_update import BoneChange, Finding

from . import dependencies, skeleton_graph, skeleton_reads
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
    scene: tuple[Any, ...] = ()
    skin: Any = None

    def require(self, document: Any) -> None:
        self.records.require(document)
        graph = dependencies.graph(document)
        if document.attachments_enabled != self.attachments_enabled:
            raise ObsoleteInputs("Attachment evaluation settings changed; prepare again.")
        skeleton_reads.require_global(self, document)
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
    mappings: tuple[Any, ...] = ()
    required: tuple[Any, ...] = ()
    publication_resources: Any = None

    @property
    def ready(self) -> bool:
        return not any(row.blocking for row in self.findings)

    def merge(self, current: Any) -> Any:
        self.reads.require(current)
        if current is self.baseline:
            return self.document
        updates = self.merged_groups(current)
        if self.document.skin != self.baseline.skin:
            updates["skin"] = self.document.skin
        updates["shortcut_order"] = skeleton_reads.merge_order(self, current)
        return replace(current, **updates)

    def merged_groups(self, current: Any) -> Any:
        return {
            name: apply_records(
                getattr(current, name),
                getattr(self.baseline, name),
                getattr(self.document, name),
                rows,
            )
            for name, rows in self.changed().items()
        }

    def changed(self) -> dict[str, tuple[Any, ...]]:
        return {
            name: changed_records(getattr(self.baseline, name), getattr(self.document, name))
            for name in GROUPS
        }


def changed_records(before: Any, after: Any) -> tuple[Any, ...]:
    records = {skeleton_graph.identity(item): item for item in before}
    return tuple(item for item in after if records.get(skeleton_graph.identity(item)) != item)


def apply_records(current: Any, before: Any, after: Any, rows: Any) -> Any:
    removed = {skeleton_graph.identity(v) for v in before} - {
        skeleton_graph.identity(v) for v in after
    }
    retained = tuple(v for v in current if skeleton_graph.identity(v) not in removed)
    return skeleton_graph.merge_records(retained, rows)


def reads(context: Any, seeds: set[Port], extra: set[str]) -> Reads:
    graph = dependencies.graph(context.document)
    affected = dependencies.closure(dependencies.reverse(graph), seeds)
    required = dependencies.closure(graph, affected)
    keys = skeleton_reads.keys(context, required, extra)
    original = dependencies.graph(context.baseline)
    return Reads(
        readset(context.baseline, keys),
        skeleton_reads.relationships(original, affected),
        context.baseline.attachments_enabled,
        skeleton_reads.observed_scene(context, required),
        context.baseline.skin if context.baseline.skin.reference else None,
    )
