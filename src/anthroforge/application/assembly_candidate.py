"""A prepared independent graph, merged into the current destination in one transaction."""

from dataclasses import dataclass, field, replace
from typing import Any, cast

from anthroforge.core.assembly import ExternalReference, ImportProvenance
from anthroforge.core.document import Document
from anthroforge.core.jobs import ObsoleteInputs
from anthroforge.core.results import Port
from anthroforge.core.tissues import TissueVCP

from .assembly_result_state import CHANGED
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
            if read_record(document, key) != value:
                raise ObsoleteInputs("A mapped destination changed; prepare the import again.")


def read_record(document: Any, key: str) -> Any:
    if key.startswith("formula-result:"):
        return document.formula_index.results.get(key.removeprefix("formula-result:"))
    if key.startswith("mirror:"):
        return document.mirrors.rules.get(key.removeprefix("mirror:"))
    if key.startswith("external:"):
        return next((r for r in document.external_references if r.id == key[9:]), None)
    if key == "formula_writers":
        return tuple(
            (f.id, f.target) for d in document.driving_shortcuts for f in d.formulas if f.enabled
        )
    return next(
        (v for v in (*document.driving_shortcuts, *document.shortcuts) if v.id == key),
        document.registry.records.get(key),
    )


def readset(document: Any, keys: set[str], empty: bool = False) -> ReadSet:
    from .assembly_placement import frame_reads

    return ReadSet(
        str(document.id),
        tuple((key, read_record(document, key)) for key in sorted(frame_reads(document, keys))),
        empty,
    )


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
    prepared_from: Document | None = field(default=None, repr=False, compare=False)
    prepared_document: Document | None = field(default=None, repr=False, compare=False)

    @property
    def ready(self) -> bool:
        return not any(v.get("blocking", False) for v in self.findings)

    def merge(self, document: Document) -> Document:
        self.reads.require(document)
        if document is self.prepared_from and self.prepared_document is not None:
            return self.prepared_document
        changes: dict[str, Any] = {
            key: (*getattr(document, key), *value) for key, value in self.additions.items()
        }
        changes["imports"] = (*document.imports, self.provenance)
        changes["external_references"] = (*document.external_references, *self.references)
        return replace(document, **changes)


def install(session: Any, candidate: Candidate) -> dict[str, Any]:
    if not candidate.ready:
        raise ValueError("Resolve the blocking import findings before importing.")
    require_workspace(session, candidate)
    updated = candidate.merge(session.document)
    for kind in Resources.__dataclass_fields__:
        getattr(session.resources, kind).update(getattr(candidate.resources, kind))
    adopt(session, candidate, updated)
    return installed(session, candidate)


def adopt(session: Any, candidate: Any, updated: Document) -> None:
    keys = (
        *candidate.additions,
        "external_references",
        "_index",
        "_registry",
        "_mirrors",
        "_formulas",
    )
    if isinstance(candidate, Candidate):
        keys += ("imports",)
    session.replace_document(
        accepted_outputs=accepted_outputs(candidate), **{key: getattr(updated, key) for key in keys}
    )


def prepared[T](candidate: T, document: Document) -> T:
    value = cast(Any, candidate)
    return cast(T, replace(value, prepared_from=document, prepared_document=value.merge(document)))


def require_workspace(session: Any, candidate: Any) -> None:
    from .workspace_policy import included

    if isinstance(candidate, Candidate):
        keys = {v.parent for v in candidate.additions.get("entities", ())}
    else:
        keys = {use.owner for r in candidate.references for use in r.uses}
    for key in keys & session.document.registry.records.keys():
        if not included(session.document, session.workspace, key):
            raise ValueError("Choose a destination or reference owner in the current workspace.")


def installed(session: Any, candidate: Any) -> dict[str, Any]:
    from . import assembly_result_state, presentation

    if isinstance(candidate, Candidate):
        presentation.include_created(
            session, set(candidate.identities.values()) & session.document.registry.records.keys()
        )
    jobs = assembly_result_state.schedule(session, candidate)
    provenance = candidate.provenance.id if isinstance(candidate, Candidate) else ""
    return dict(identities=candidate.identities, provenance=provenance, jobs=jobs)


def accepted_outputs(candidate: Any) -> frozenset[Port]:
    formulas = {
        Port(r.formula, "formula")
        for r in candidate.additions.get("formula_results", ())
        if r.status != "pending" and r.error != CHANGED
    }
    tissues = {
        Port(v.id, "final")
        for v in candidate.additions.get("objects", ())
        if isinstance(v, TissueVCP) and v.final_result.status != "pending"
    }
    return frozenset(formulas | tissues)
