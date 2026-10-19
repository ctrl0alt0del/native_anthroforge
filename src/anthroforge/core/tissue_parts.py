"""Parts are keyed by stable construction identity; inactive settings remain authored."""

from dataclasses import replace

from .tissue_settings import TissuePart
from .tissues import TissueVCP


def active(item: TissueVCP) -> tuple[TissuePart, ...]:
    values = {p.id: p for p in item.parts}
    return tuple(values.get(key, replace(item.parts[0], id=key)) for key in item.base_state.parts)


def installed(item: TissueVCP, parts: tuple[TissuePart, ...]) -> tuple[TissuePart, ...]:
    keys = {p.id for p in parts}
    return (*parts, *(p for p in item.parts if p.id not in keys))
