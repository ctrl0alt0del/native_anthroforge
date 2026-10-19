"""Automatic attachment searches cannot capture a surface generated from the same path."""

from anthroforge.core import anatomical_surfaces
from anthroforge.core.document import Document
from anthroforge.core.results import Port
from anthroforge.core.surface_references import SurfaceReference

from . import dependencies, surface_providers


def eligible(document: Document, curve: str) -> tuple[SurfaceReference, ...]:
    downstream = dependencies.affected(document, {Port(curve, "path")})
    return tuple(
        sorted(
            ref
            for ref in surface_providers.references(document)
            if ref.role != "TISSUE_BASE"
            and ref.target not in downstream
            and anatomical_surfaces.usable(
                anatomical_surfaces.result(document.registry.anatomy[ref.target], ref.role)
            )
        )
    )
