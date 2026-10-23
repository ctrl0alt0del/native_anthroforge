"""Ownership follows controlled properties, never ordinary attachment propagation."""

from typing import Any

from anthroforge.core.numeric_properties import PropertyRef, overlaps
from anthroforge.core.shortcuts import DrivingShortcut, Shortcut


def property_owners(document: Any, target: str) -> set[str]:
    pending, seen, owners = [target], set[str](), set[str]()
    while pending:
        key = pending.pop()
        if key in seen:
            continue
        seen.add(key)
        if key in document.registry.anatomy:
            owners.add(key)
        elif key in document.registry.records:
            owners.update(getattr(document.object(key), "owners", ()))
            pending.extend(document.registry.consumers.get(key, ()))
    return owners.intersection(document.registry.anatomy)


def targets(document: Any, shortcut: Shortcut | DrivingShortcut) -> set[str]:
    if isinstance(shortcut, Shortcut):
        return {shortcut.reference.target}
    pending, seen, result = [shortcut.id], set[str](), set[PropertyRef]()
    drivers = {v.id: v for v in document.driving_shortcuts}
    while pending:
        key = pending.pop()
        if key in seen or key not in drivers:
            continue
        seen.add(key)
        result.update(f.target for f in drivers[key].formulas if f.enabled)
        pending.extend(d.id for d in drivers.values() if consumes(d, key, result))
    return {reference.target for reference in result}


def consumes(driver: DrivingShortcut, source: str, properties: set[PropertyRef]) -> bool:
    return any(
        i.driver == source
        or (i.property is not None and any(overlaps(i.property, p) for p in properties))
        for formula in driver.formulas
        if formula.enabled
        for i in formula.inputs
    )


def owners(document: Any, shortcut: Shortcut | DrivingShortcut) -> set[str]:
    return set().union(
        *(property_owners(document, target) for target in targets(document, shortcut))
    )


def scp_owner(document: Any, shortcut: Shortcut | DrivingShortcut) -> str:
    values = owners(document, shortcut)
    return (
        next(iter(values)) if len(values) == 1 and values <= document.index.entities.keys() else ""
    )


def attachment_scope(document: Any, shortcut: Shortcut | DrivingShortcut) -> str:
    """Explicit policy scope does not alter inferred ownership or UI grouping."""
    return shortcut.policy.scope or scp_owner(document, shortcut)
