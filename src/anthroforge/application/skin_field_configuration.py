"""FIELD policy adapters; generic jobs never validate collagen or gap parameters."""

from dataclasses import replace
from typing import Any

from anthroforge.core import skin_field

FIELDS = frozenset(skin_field.FieldContributor.__dataclass_fields__) - {"owner"}


def configure(config: Any, values: dict[str, Any]) -> Any:
    return replace(config, settings=replace(config.settings, **values))


def contributor(config: Any, owner: str) -> Any:
    return next(
        (r for r in config.contributors if r.owner == owner), skin_field.FieldContributor(owner)
    )


def configure_contributor(config: Any, owner: str, values: dict[str, Any]) -> Any:
    changed = replace(contributor(config, owner), **values)
    rows = {r.owner: r for r in config.contributors} | {owner: changed}
    return replace(config, contributors=tuple(rows.values()))


def resources(record: Any) -> set[str]:
    return {row.get("painted", "") for row in record.values().get("contributors", ())} - {""}


def inputs(document: Any) -> set[Any]:
    from anthroforge.core import skin_sources

    from .skin_inputs import source_ports

    return set().union(*(source_ports(row) for row in skin_sources.contributors(document)))


def reason(document: Any) -> str:
    from anthroforge.core import skin_sources

    return "" if skin_sources.contributors(document) else "Add SCP or tissue geometry first."
