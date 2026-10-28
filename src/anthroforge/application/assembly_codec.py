"""Project-owned assembly records; no source file is required after import."""

from typing import Any

from anthroforge.core.assembly import ExternalReference, ImportProvenance, ReferenceUse


def decode(data: dict[str, Any]) -> dict[str, Any]:
    return dict(
        imports=tuple(provenance(row) for row in data.pop("imports", ())),
        external_references=tuple(reference(row) for row in data.pop("external_references", ())),
    )


def provenance(row: dict[str, Any]) -> ImportProvenance:
    return ImportProvenance(
        **(row | {key: tuple(map(tuple, row.get(key, ()))) for key in ("identities", "mappings")})
    )


def reference(row: dict[str, Any]) -> ExternalReference:
    return ExternalReference(
        **(row | dict(uses=tuple(ReferenceUse(**v) for v in row.get("uses", ()))))
    )
