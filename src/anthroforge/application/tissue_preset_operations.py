"""Existing-tissue preset resets preserve user-owned construction and relationship intent."""

from dataclasses import replace
from typing import Any

from anthroforge.core import tissue_policy, tissue_presets

from . import object_operations, tissue_operations


def apply(session: Any, target: str, preset: str) -> None:
    item = tissue_operations.tissue(session, target)
    source = session.document.object(item.source)
    updated = candidate(item, tissue_presets.settings(source, preset), preset)
    tissue_policy.validate(updated, session.document.registry.records)
    tissue_operations.require_inflation_topology(session, item, updated)
    require_field_layout(item, updated)
    object_operations.install(session, updated)


def candidate(item: Any, defaults: dict[str, Any], preset: str) -> Any:
    inflation = defaults["parts"][0].a.inflation
    parts = tuple(
        replace(p, a=replace(p.a, inflation=inflation), b=replace(p.b, inflation=inflation))
        for p in item.parts
    )
    custom = tuple(row for row in item.constraints if row.origin == "CUSTOM")
    constraints = merged_constraints(custom, defaults["constraints"])
    return replace(
        item, preset=preset, parts=parts, relaxation=defaults["relaxation"], constraints=constraints
    )


def merged_constraints(custom: tuple[Any, ...], defaults: tuple[Any, ...]) -> tuple[Any, ...]:
    for row in defaults:
        if any(conflicting(row, existing) for existing in custom):
            raise ValueError(
                "Preset conflicts with a custom Fixed region; edit that region explicitly."
            )
    generated = tuple(row for row in defaults if not any(equivalent(row, c) for c in custom))
    return (*custom, *generated)


def conflicting(first: Any, second: Any) -> bool:
    return (
        first.mask == second.mask
        and first.mode == second.mode == "FIXED"
        and (first.offset != second.offset or second.reference is not None)
    )


def equivalent(first: Any, second: Any) -> bool:
    fields = ("mask", "mode", "strength", "feather", "offset", "reference")
    return all(getattr(first, name) == getattr(second, name) for name in fields)


def require_field_layout(before: Any, after: Any) -> None:
    def layout(item: Any) -> tuple[Any, ...]:
        return tuple(
            (p.id, s.inflation.mode, s.inflation.segments) for p in item.parts for s in (p.a, p.b)
        )

    bound_fields = before.fields or any(row.binding_asset for row in before.constraints)
    if bound_fields and layout(before) != layout(after):
        raise ValueError(
            "This preset changes the field layout; custom fields and regions must remain intact."
        )
