"""Declared missing inputs fail locally; retained source display is not a new accepted solve."""

from typing import Any

from anthroforge.core.results import Port


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
