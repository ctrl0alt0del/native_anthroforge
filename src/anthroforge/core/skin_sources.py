"""Document-wide contributor identities, independent of selection and workspace display."""

from dataclasses import dataclass
from typing import Any

from .entities import SCP
from .fibers import Fiber
from .results import geometry_asset
from .tissues import TissueVCP


@dataclass(frozen=True, slots=True, order=True)
class Source:
    owner: str
    kind: str
    instance: str = ""


def kind(item: Any) -> str:
    if isinstance(item, SCP) and (item.primitive or geometry_asset(item)):
        return "SCP"
    if isinstance(item, TissueVCP):
        return "TISSUE"
    return "FIBER" if isinstance(item, Fiber) else ""


def candidates(document: Any) -> tuple[Source, ...]:
    source = [
        Source(item.id, kind(item)) for item in document.registry.records.values() if kind(item)
    ]
    mirrored = [
        Source(value.source, kind(document.object(value.source)), value.rule)
        for value in document.mirrors.instances.values()
        if kind(document.object(value.source))
    ]
    return tuple(sorted((*source, *mirrored)))


def contributors(document: Any) -> tuple[Source, ...]:
    """Physical draft/deformation sources never fall back to construction objects."""
    return tuple(source for source in candidates(document) if source.kind != "FIBER")


def guides(document: Any) -> tuple[Source, ...]:
    flow = {row.owner for row in document.skin.contributors if row.flow}
    return tuple(
        source
        for source in candidates(document)
        if source.kind == "FIBER" and (document.object(source.owner).closed or source.owner in flow)
    )
