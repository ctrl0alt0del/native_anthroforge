"""Shared review inventory for retained wrappers and formula references."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.shortcuts import implicit_identity


def rows(document: Any) -> list[dict[str, Any]]:
    found = [entry(s.reference, s.id, "shortcut", s.label or s.id) for s in document.shortcuts]
    for driver in document.driving_shortcuts:
        for formula in driver.formulas:
            found.append(entry(formula.target, formula.id, "formula", driver.label + " · output"))
            found.extend(
                entry(i.property, formula.id, "input", driver.label + " · " + i.name)
                for i in formula.inputs
                if i.property is not None
            )
    return found


def entry(reference: Any, control: str, kind: str, label: str) -> dict[str, Any]:
    return dict(
        key=implicit_identity(reference),
        control=control,
        kind=kind,
        name=label,
        property=asdict(reference),
        owner=reference.target,
    )
