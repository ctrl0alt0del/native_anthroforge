"""Prepare one selected graph; unresolved references remain explicit and repairable."""

from dataclasses import dataclass, field, replace
from typing import Any

from anthroforge.core import graph_records

from . import (
    assembly_bindings,
    assembly_copy,
    assembly_graph,
    assembly_mirrors,
    assembly_resources,
    assembly_result_state,
    assembly_snapshots,
)
from .assembly_candidate import Candidate, ReadSet
from .assembly_mapping import Mappings
from .assembly_placement import Placement, frame_reads
from .resources import Resources


@dataclass
class Preparation:
    source: Any
    destination: Any
    available: Resources
    engine: Any
    cancel: Any
    options: dict[str, Any]
    selection: Any = None
    mapping: Any = None
    ids: dict[str, str] = field(default_factory=dict)
    assets: dict[str, str] = field(default_factory=dict)
    resources: Resources = field(default_factory=Resources)
    loaded: Resources = field(default_factory=Resources)
    values: dict[str, tuple[Any, ...]] = field(default_factory=dict)
    parent: str = ""
    evidence: tuple[dict[str, Any], ...] = ()

    def run(self, keys: list[str]) -> Candidate:
        self.select(keys)
        self.copy()
        roots = assembly_graph.roots(self.selection)
        self.parent = assembly_copy.destination_parent(
            self.destination, self.options.get("parent", ""), bool(roots)
        )
        assembly_copy.hierarchy(self.values, self.selection, self.ids, self.parent)
        candidate = self.candidate()
        if candidate.ready:
            self.evidence = assembly_bindings.assess(self, candidate)
            assembly_result_state.mark(self)
        return self.candidate()

    def select(self, keys: list[str]) -> None:
        mappings = self.options.get("mappings", {})
        attached = self.options.get("include_attached_tissues", False)
        self.selection, rows = assembly_copy.selected(self.source, keys, attached, mappings)
        self.loaded = assembly_resources.load(self.source, self.selection, self.engine, self.cancel)
        self.ids = assembly_graph.identities(self.selection, self.loaded)
        assembly_mirrors.allocate(self.source.document, self.selection, self.ids)
        self.mapping = Mappings(self.source, self.destination, self.ids, mappings)
        self.mapping.assess(tuple(row for row in rows if row.source not in self.ids))
        self.resources, self.assets = assembly_resources.transfer(self.loaded, self.ids)
        assembly_snapshots.retain(self)

    def copy(self) -> None:
        values = assembly_copy.source_records(self.source.document, self.selection)
        placement = Placement(self.engine, self.source.document, self.destination, self.mapping)
        for group, rows in values.items():
            self.values[group] = tuple(self.record(item, placement) for item in rows)
        self.resource_metadata(placement)
        self.mirrors()

    def mirrors(self) -> None:
        document = self.source.document
        self.values["mirror_rules"] = assembly_mirrors.copy(document, self.selection, self.ids)
        self.values["shared_mirror_targets"] = assembly_mirrors.shared(document, self.ids)

    def record(self, item: Any, placement: Placement) -> Any:
        changed = graph_records.rewritten(item, self.ids, self.assets)
        if not hasattr(item, "id"):
            return changed
        return placement.apply(item, self.mapping.patch(item, changed))

    def resource_metadata(self, placement: Placement) -> None:
        # Accepted path definitions own identities and relationships too.
        for key, path in self.loaded.paths.items():
            value = self.resources.paths[self.assets[key]]
            self.resources.paths[self.assets[key]] = replace(
                value, authored=self.record(path.authored, placement)
            )
        self.attachment_metadata()

    def attachment_metadata(self) -> None:
        for key, value in self.loaded.attachments.items():
            targets = tuple(
                replace(
                    t,
                    reference=self.mapping.surface(t.reference),
                    material_asset=self.assets[t.material_asset],
                )
                for t in value.targets
            )
            self.resources.attachments[self.assets[key]] = replace(value, targets=targets)

    def candidate(self) -> Candidate:
        mapped = tuple((r.source_entity, r.target) for r in self.mapping.references if r.target)
        provenance = assembly_copy.provenance(self.source, self.ids, mapped)
        return Candidate(
            self.values,
            self.resources,
            self.ids,
            provenance,
            tuple(self.mapping.references),
            self.readset(),
            tuple(self.mapping.findings),
            evidence=self.evidence,
            selection=self.selection.reasons,
            mappings=tuple(self.mapping.rows),
        )

    def readset(self) -> ReadSet:
        targets = self.mapping.reads | ({self.parent} if self.parent else set())
        reads = tuple(
            (key, self.destination.object(key))
            for key in sorted(frame_reads(self.destination, targets))
        )
        empty = bool(assembly_graph.roots(self.selection)) and not self.destination.entities
        return ReadSet(str(self.destination.id), reads, empty)


def prepare(
    source: Any, keys: Any, options: Any, engine: Any, payload: Any, cancel: Any
) -> Candidate:
    destination, available = payload
    return Preparation(source, destination, available, engine, cancel, options).run(keys)
