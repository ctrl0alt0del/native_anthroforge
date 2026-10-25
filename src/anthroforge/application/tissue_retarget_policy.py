"""Retargeting proposes explicit, capability-driven changes without anatomical algorithm labels."""

from dataclasses import dataclass, field, replace
from typing import Any

from anthroforge.core import tissue_policy, tissue_presets
from anthroforge.core.membranes import Membrane
from anthroforge.core.replacement_reviews import Change
from anthroforge.core.tissue_settings import TissuePart

GRID_MODES = frozenset(("CTRL_POINT", "DISTRIBUTED", "SECTION_PROFILE"))


@dataclass
class Edits:
    target: str
    rows: list[Change] = field(default_factory=list)

    def note(self, key: str, description: str, target: str = "") -> None:
        self.rows.append(Change(key, target or self.target, "RETARGET_SETTING", description))


def prepare(item: Any, source: Any, records: Any, edits: Edits) -> Any:
    allowed = set(tissue_policy.inflation_modes(source))
    closed = isinstance(source, Membrane) and any(records[u.curve].closed for u in source.curves)
    if closed:
        allowed.discard("SECTION_PROFILE")
    default = tissue_presets.mode(source, item.preset)
    parts = tuple(part(p, allowed, default, edits) for p in item.parts)
    updated = replace(item, source=source.id, parts=parts)
    two_sided = isinstance(source, Membrane) and not source.close_across and not closed
    updated = strategy_changes(updated, source, edits, two_sided)
    return compatible_regions(updated, edits)


def part(item: TissuePart, allowed: set[str], default: str, edits: Edits) -> TissuePart:
    sides = {
        key: side(getattr(item, key), allowed, default, edits, item.id + "/" + key)
        for key in ("a", "b")
    }
    return replace(item, **sides)


def side(item: Any, allowed: set[str], default: str, edits: Edits, key: str) -> Any:
    inflation, smoothing = item.inflation, item.smoothing
    if inflation.mode not in allowed:
        edits.note(
            "mode:" + key, "Use " + default + " inflation for " + key + "; retain other values."
        )
        inflation = replace(inflation, mode=default)
    if inflation.mode not in GRID_MODES and smoothing.mode != "OFF":
        edits.note("smoothing:" + key, "Disable unsupported height smoothing for " + key + ".")
        smoothing = replace(smoothing, mode="OFF")
    return replace(item, inflation=inflation, smoothing=smoothing)


def strategy_changes(item: Any, source: Any, edits: Edits, two_sided: bool) -> Any:
    modes = {p.a.inflation.mode for p in item.parts}
    surface = tissue_policy.domain(source) == "SURFACE"
    if item.relaxation.mode != "NONE" and modes & GRID_MODES:
        edits.note(
            "relaxation", "Disable relaxation for muscle-grid inflation; retain its parameters."
        )
        item = replace(item, relaxation=replace(item.relaxation, mode="NONE"))
    if item.crop.enabled and modes - GRID_MODES:
        edits.note("crop", "Disable the unsupported material crop; retain its plane settings.")
        item = replace(item, crop=replace(item.crop, enabled=False))
    if item.both_sides and (not two_sided or modes - GRID_MODES):
        edits.note("both_sides", "Disable unsupported two-sided composition.")
        item = replace(item, both_sides=False)
    return stacking_changes(item, surface, edits)


def stacking_changes(item: Any, surface: bool, edits: Edits) -> Any:
    if not surface and item.stacking:
        edits.note(
            "stacking", "Disable stacking for this non-surface construction; keep its settings."
        )
        item = replace(item, stacking=False)
    if not surface and item.stack_relationships:
        edits.note(
            "stack_relationships", "Remove stacking relationships from this non-surface tissue."
        )
        item = replace(item, stack_relationships=())
    return item


def compatible_regions(item: Any, edits: Edits) -> Any:
    fields = compatible_fields(item, edits)
    item = replace(item, fields=fields)
    masks = set(tissue_policy.region_masks(item))
    for row in item.constraints:
        if row.mask not in masks:
            edits.note(
                "constraint:" + row.id, "Discard region using unavailable mask " + row.mask + "."
            )
    return replace(item, constraints=tuple(r for r in item.constraints if r.mask in masks))


def compatible_fields(item: Any, edits: Edits) -> tuple[Any, ...]:
    modes = {p.a.inflation.mode for p in item.parts}
    fields = tuple(f for f in item.fields if f.name != "INFLATION" or modes == {"NORMAL"})
    for value in item.fields:
        if value not in fields:
            edits.note(
                "field:" + value.name, "Discard unsupported inflation field " + value.name + "."
            )
    return fields
