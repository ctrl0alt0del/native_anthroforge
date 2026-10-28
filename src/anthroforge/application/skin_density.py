"""Worker preparation of anatomical ownership and exclusive topology budgets."""

from dataclasses import dataclass
from typing import Any

from anthroforge.core import skin_budgets
from anthroforge.native import skin_density as native
from anthroforge.native import skin_ownership as ownership

from . import skin_ownership, skin_refinement


@dataclass(frozen=True)
class Field:
    ownership: ownership.Ownership
    regions: Any
    density: native.Density
    plan: skin_budgets.Plan
    warnings: tuple[str, ...]
    refinement: dict[str, Any]
    adaptive: bool


@dataclass(frozen=True)
class Assignment:
    plan: skin_budgets.Plan
    support: skin_ownership.Supports
    owners: ownership.Ownership
    regions: Any


def evaluate(document: Any, captured: Any, mesh: Any, cancel: int = 0) -> Field:
    plan = skin_budgets.plan(document)
    support = skin_ownership.capture(document, captured.sources, plan.owners)
    owners = ownership.evaluate(
        mesh, captured.geometry, support.offsets, support.bones, support.candidates, cancel=cancel
    )
    ids = ownership.regions(
        mesh.engine, owners.owners, plan.owner_regions, len(plan.regions) - 1, cancel
    )
    return complete(document, captured, mesh, Assignment(plan, support, owners, ids), cancel)


def complete(document: Any, captured: Any, mesh: Any, assigned: Assignment, cancel: int) -> Field:
    proximity = document.skin.topology_settings.refinement != "NONE"
    budgets = [row.exclusive for row in assigned.plan.regions]
    density = native.evaluate(
        mesh, assigned.regions, budgets, iterations=0 if proximity else 8, cancel=cancel
    )
    adjusted = skin_refinement.apply(
        document, captured, assigned.support, mesh, density.lengths, cancel
    )
    if proximity:
        density = native.evaluate(
            mesh, assigned.regions, budgets, initial=adjusted.lengths, cancel=cancel
        )
    adaptive = bool(skin_budgets.explicit(document)) or adjusted.active
    return result(assigned, density, adjusted, adaptive)


def result(assigned: Assignment, density: native.Density, adjusted: Any, adaptive: bool) -> Field:
    warnings = assignment_warnings(assigned, density) + adjusted.warnings
    return Field(
        assigned.owners,
        assigned.regions,
        density,
        assigned.plan,
        warnings,
        adjusted.statistics,
        adaptive,
    )


def assignment_warnings(assigned: Assignment, density: native.Density) -> tuple[str, ...]:
    return (
        *assigned.support.warnings,
        *fallback_warning(assigned.owners),
        *unusable_regions(assigned.plan, density),
    )


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


def achieved(field: Field, envelope: Any, mesh: Any, cancel: int) -> list[dict[str, Any]]:
    owners, _ = ownership.sample(
        envelope, mesh, field.ownership.owners, field.density.lengths, cancel
    )
    counts = native.achieved(
        mesh, owners, field.plan.owner_regions, len(field.plan.regions), cancel
    )
    return budget_rows(field, counts)


def budget_rows(field: Field, counts: Any) -> list[dict[str, Any]]:
    return [
        dict(
            owner=row.owner,
            requested=row.requested,
            exclusive=row.exclusive,
            actual_exclusive_quads=int(count),
            area=float(area),
        )
        for row, count, area in zip(
            field.plan.regions, counts, field.density.region_areas, strict=True
        )
    ]


def budget_warnings(rows: Any) -> tuple[str, ...]:
    return tuple(
        f"Topology budget for {row['owner'] or 'root remainder'} resolved to "
        f"{row['actual_exclusive_quads']}/{row['exclusive']} quads."
        for row in rows
        if row["exclusive"]
        and abs(row["actual_exclusive_quads"] - row["exclusive"]) / row["exclusive"] > 0.2
    )
