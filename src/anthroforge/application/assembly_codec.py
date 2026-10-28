"""Project-owned assembly records; no source file is required after import."""

from typing import Any

from anthroforge.core.assembly import (
    ExternalReference,
    ImportProvenance,
    ReferenceUse,
    RetainedOutput,
)
from anthroforge.core.numeric_properties import decode_reference


def decode(data: dict[str, Any]) -> dict[str, Any]:
    return dict(
        imports=tuple(provenance(row) for row in data.pop("imports", ())),
        external_references=tuple(reference(row) for row in data.pop("external_references", ())),
    )


def provenance(row: dict[str, Any]) -> ImportProvenance:
    row = dict(row, outputs=tuple(RetainedOutput(**v) for v in row.get("outputs", ())))
    return ImportProvenance(
        **(row | {key: tuple(map(tuple, row.get(key, ()))) for key in ("identities", "mappings")})
    )


def reference(row: dict[str, Any]) -> ExternalReference:
    uses = tuple(
        ReferenceUse(**(v | dict(path=tuple(v.get("path", ()))))) for v in row.get("uses", ())
    )
    prop = decode_reference(row["property"]) if row.get("property") else None
    return ExternalReference(
        **(row | dict(uses=uses, property=prop, surface_frame=tuple(row.get("surface_frame", ()))))
    )
