"""Document-wide contributor identities, independent of selection and workspace display."""

from dataclasses import dataclass
from typing import Any

from .anatomical_surfaces import usable
from .entities import SCP
from .fibers import Fiber
from .results import geometry_asset
from .surfaces import Surface
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


def fiber_sources(document: Any, source: str) -> frozenset[str]:
    item = document.registry.records.get(source)
    if isinstance(item, Fiber):
        return frozenset((item.id,))
    if isinstance(item, Surface):
        return frozenset(use.curve for use in item.curves)
    return frozenset()


def selected(document: Any, available_tissues: frozenset[Source]) -> tuple[Source, ...]:
    represented = {
        (fiber, source.instance)
        for source in available_tissues
        for fiber in fiber_sources(document, document.object(source.owner).source)
    }
    return tuple(
        source
        for source in candidates(document)
        if source.kind != "FIBER" or (source.owner, source.instance) not in represented
    )


def accepted_tissues(document: Any) -> frozenset[Source]:
    return frozenset(
        source
        for source in candidates(document)
        if source.kind == "TISSUE" and usable(document.object(source.owner).final_result)
    )
