"""Declared missing inputs fail locally; retained source display is not a new accepted solve."""

from typing import Any

from anthroforge.core.assembly import declaration
from anthroforge.core.results import Port, ReadRevision


def require_inputs(document: Any, observed: frozenset[Port]) -> None:
    if not document.external_references:
        return
    owners = {port.owner for port in observed}
    missing = [r for r in document.external_references if not r.target and r.id in owners]
    if missing:
        names = ", ".join(r.name for r in missing[:8])
        raise ValueError("Resolve imported references before this calculation: " + names)


def pending(document: Any, owner: str) -> tuple[Any, ...]:
    return tuple(
        row
        for row in document.external_references
        if not row.target and any(use.owner == owner for use in row.uses)
    )


def revision(document: Any, port: Port) -> ReadRevision | None:
    reference = declaration(document.registry.records, port.owner)
    if reference is None:
        return None
    return ReadRevision(port.owner, port.output, 0, 0, ("unresolved:" + reference.id,))


def property_descriptor(document: Any, reference: Any) -> Any:
    value = declaration(document.registry.records, reference.target)
    if value is None:
        return None
    original = value.property
    if original is None or (original.path, original.component) != (
        reference.path,
        reference.component,
    ):
        raise ValueError("This property is not a declared imported reference.")
    return declared_descriptor(value, reference)


def declared_descriptor(value: Any, reference: Any) -> Any:
    from anthroforge.core.numeric_properties import NumericDescriptor

    return NumericDescriptor(
        reference,
        value.name,
        value.numeric_type,
        value.dimension,
        value.components,
        writable=False,
        reason="Resolve the imported property reference first.",
        vector=value.components > 1,
    )
