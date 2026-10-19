"""Shared validated edits for tissue relaxation, fields and region constraints."""

from dataclasses import replace
from typing import Any

from anthroforge.core import tissue_policy
from anthroforge.core.tissue_constraints import TissueConstraint, TissueField
from anthroforge.core.tissue_settings import TissueRelaxation

from . import object_operations, tissue_fields
from .tissue_operations import tissue


def install(session: Any, item: Any) -> None:
    tissue_policy.validate(item, session.document.registry.records)
    object_operations.install(session, item)


def relaxation(session: Any, target: str, changes: dict[str, Any]) -> None:
    item = tissue(session, target)
    allowed = set(TissueRelaxation.__dataclass_fields__)
    if set(changes) - allowed:
        raise ValueError("Unknown tissue relaxation setting.")
    if "gravity" in changes:
        changes = dict(changes, gravity=tuple(changes["gravity"]))
    install(session, replace(item, relaxation=replace(item.relaxation, **changes)))


def constraint_add(
    session: Any, target: str, mask: str = "ALL", mode: str = "FIXED", **settings: Any
) -> str:
    item = tissue(session, target)
    row = TissueConstraint(mask=mask, mode=mode, **settings)
    require_source_constraint(row)
    install(session, replace(item, constraints=(*item.constraints, row)))
    return row.id


def constraint_update(session: Any, target: str, constraint: str, changes: dict[str, Any]) -> None:
    item = tissue(session, target)
    row = next((r for r in item.constraints if r.id == constraint), None)
    if row is None:
        raise ValueError("Unknown tissue constraint.")
    if set(changes) - {"mask", "mode", "strength", "feather", "offset"}:
        raise ValueError("Use explicit rebind to change a constraint target.")
    updated = replace(row, **changes)
    install(
        session,
        replace(
            item, constraints=tuple(updated if r.id == constraint else r for r in item.constraints)
        ),
    )


def constraint_remove(session: Any, target: str, constraint: str) -> None:
    item = tissue(session, target)
    rows = tuple(r for r in item.constraints if r.id != constraint)
    if len(rows) == len(item.constraints):
        raise ValueError("Unknown tissue constraint.")
    install(session, replace(item, constraints=rows))


def require_source_constraint(row: TissueConstraint) -> None:
    if row.reference is not None or row.bindings:
        raise ValueError("Use explicit region capture for target-relative constraints.")


def field_set(
    session: Any, target: str, name: str, values: list[float], domain: str = "BASE"
) -> None:
    item = tissue(session, target)
    count, signature = tissue_fields.domain(session.resources, item, domain)
    if len(values) != count:
        raise ValueError(f"The {domain.lower()} field requires {count} explicit weights.")
    value = TissueField(name, tuple(values), topology=signature, domain=domain)
    existing = tuple(f for f in item.fields if f.name != name)
    install(session, replace(item, fields=(*existing, value)))


def field_remove(session: Any, target: str, name: str) -> None:
    item = tissue(session, target)
    if any(r.mask == name for r in item.constraints):
        raise ValueError("Remove or change the constraints using this field first.")
    install(session, replace(item, fields=tuple(f for f in item.fields if f.name != name)))
