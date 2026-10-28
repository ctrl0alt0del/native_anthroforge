"""A prepared independent graph, merged into the current destination in one transaction."""

from dataclasses import dataclass, field, replace
from typing import Any

from anthroforge.core.assembly import ExternalReference, ImportProvenance
from anthroforge.core.document import Document
from anthroforge.core.jobs import ObsoleteInputs

from .resources import Resources


@dataclass(frozen=True)
class ReadSet:
    document: str
    records: tuple[tuple[str, Any], ...] = ()
    empty_hierarchy: bool = False

    def require(self, document: Document) -> None:
        if str(document.id) != self.document:
            raise ObsoleteInputs("The destination project changed; prepare the import again.")
        if self.empty_hierarchy and document.entities:
            raise ObsoleteInputs("The destination now has anatomy; choose an import parent.")
        for key, value in self.records:
            if document.registry.records.get(key) != value:
                raise ObsoleteInputs("A mapped destination changed; prepare the import again.")


@dataclass(frozen=True)
class Candidate:
    additions: dict[str, tuple[Any, ...]]
    resources: Resources
    identities: dict[str, str]
    provenance: ImportProvenance
    references: tuple[ExternalReference, ...]
    reads: ReadSet
    findings: tuple[dict[str, Any], ...] = ()
    evidence: tuple[dict[str, Any], ...] = ()
    selection: dict[str, str] = field(default_factory=dict)
    mappings: tuple[dict[str, Any], ...] = ()

    @property
    def ready(self) -> bool:
        return not any(v.get("blocking", False) for v in self.findings)

    def merge(self, document: Document) -> Document:
        self.reads.require(document)
        changes: dict[str, Any] = {
            key: (*getattr(document, key), *value) for key, value in self.additions.items()
        }
        changes["imports"] = (*document.imports, self.provenance)
        changes["external_references"] = (*document.external_references, *self.references)
        return replace(document, **changes)


def install(session: Any, candidate: Candidate) -> dict[str, Any]:
    if not candidate.ready:
        raise ValueError("Resolve the blocking import findings before importing.")
    updated = candidate.merge(session.document)
    for kind in Resources.__dataclass_fields__:
        getattr(session.resources, kind).update(getattr(candidate.resources, kind))
    keys = (*candidate.additions, "imports", "external_references")
    session.replace_document(**{key: getattr(updated, key) for key in keys})
    return dict(identities=candidate.identities, provenance=candidate.provenance.id, jobs=[])
