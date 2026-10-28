"""Persisted missing import relationships stay actionable without requesting geometry work."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.issues import Issue, evidence, fingerprint

from .providers import Provider


def source(document: Any, scope: str) -> Any:
    return tuple(asdict(row) for row in document.external_references)


def check(document: Any, scope: str, cancel: Any) -> tuple[Issue, ...]:
    return tuple(finding(row) for row in document.external_references if not row.target)


def finding(row: Any) -> Issue:
    owners = tuple(dict.fromkeys(use.owner for use in row.uses))
    return Issue(
        "assembly.v1",
        "document",
        "UNRESOLVED_IMPORT_REFERENCE",
        "Resolve imported reference: " + row.name,
        target=owners[0] if owners else "",
        related=owners,
        kind="ASSEMBLY",
        source=fingerprint(asdict(row)),
        local_key=row.id,
        details="Imported geometry is retained; calculations needing this reference are blocked.",
        evidence=evidence(reference=row.id, source_document=row.source_document, uses=asdict(row)),
    )


def provider() -> Provider:
    return Provider(
        "assembly.v1",
        lambda _: {"document"},
        lambda d, c: {"document"} if "external_references" in c.document else set(),
        source,
        check,
    )
