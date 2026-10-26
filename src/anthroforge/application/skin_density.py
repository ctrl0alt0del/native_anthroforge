"""Worker preparation of anatomical ownership and exclusive topology budgets."""

from dataclasses import dataclass
from typing import Any

from anthroforge.core import skin_budgets
from anthroforge.native import skin_density as native
from anthroforge.native import skin_ownership as ownership

from . import skin_ownership


@dataclass(frozen=True)
class Field:
    ownership: ownership.Ownership
    regions: Any
    density: native.Density
    plan: skin_budgets.Plan
    warnings: tuple[str, ...]


def evaluate(document: Any, captured: Any, mesh: Any, cancel: int = 0) -> Field:
    plan = skin_budgets.plan(document)
    support = skin_ownership.capture(document, captured.sources, plan.owners)
    owners = ownership.evaluate(
        mesh, captured.geometry, support.offsets, support.bones, support.candidates, cancel=cancel
    )
    ids = ownership.regions(
        mesh.engine, owners.owners, plan.owner_regions, len(plan.regions) - 1, cancel
    )
    density = native.evaluate(mesh, ids, [row.exclusive for row in plan.regions], cancel=cancel)
    warnings = (*support.warnings, *fallback_warning(owners), *unusable_regions(plan, density))
    return Field(owners, ids, density, plan, warnings)


def fallback_warning(owners: ownership.Ownership) -> tuple[str, ...]:
    if owners.fallback_count:
        return (f"Used nearest-SCP fallback for {owners.fallback_count} skin vertices.",)
    return ()


def unusable_regions(plan: skin_budgets.Plan, density: native.Density) -> tuple[str, ...]:
    return tuple(
        f"Topology budget for {row.owner or 'root remainder'} has no usable area or budget."
        for row, bad in zip(plan.regions, density.unusable, strict=True)
        if bad
    )
