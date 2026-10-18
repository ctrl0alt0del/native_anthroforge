"""Independent copies preserve junctions only within the explicitly copied set."""

from typing import Any
from uuid import uuid4

from anthroforge.core.junctions import Junction, PointRef, members


def identities(document: Any, mapping: dict[str, str]) -> dict[str, str]:
    links = members(document.objects)
    shared = {
        j.id: str(uuid4())
        for j in document.junctions
        if j.source.curve in mapping and sum(p.curve in mapping for p in links[j.id]) >= 2
    }
    return {**mapping, **shared}


def records(document: Any, mapping: dict[str, str]) -> tuple[Junction, ...]:
    return tuple(
        Junction(PointRef(mapping[j.source.curve], mapping[j.source.point]), mapping[j.id])
        for j in document.junctions
        if j.id in mapping
    )
