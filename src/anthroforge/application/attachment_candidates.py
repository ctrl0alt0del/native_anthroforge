"""Automatic attachment searches cannot capture a surface generated from the same path."""

from anthroforge.core.document import Document
from anthroforge.core.results import Port, geometry_asset

from . import dependencies


def eligible(document: Document, curve: str) -> tuple[str, ...]:
    downstream = dependencies.affected(document, {Port(curve, "path")})
    return tuple(
        sorted(
            item.id
            for item in document.entities
            if geometry_asset(item) and item.id not in downstream
        )
    )
