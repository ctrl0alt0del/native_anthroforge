"""Driving shortcut and formula authoring, with no evaluation side effects in expressions."""

from dataclasses import asdict, replace
from typing import Any, cast

from anthroforge.core.shortcuts import DrivingFormula, DrivingShortcut

from . import property_catalog, shortcut_codec, shortcut_operations, shortcut_ownership
from .property_guards import validate_writers


def selected(session: Any, driver: str) -> DrivingShortcut:
    value = next((d for d in session.document.driving_shortcuts if d.id == driver), None)
    if value is None:
        raise ValueError("Unknown driving shortcut.")
    return cast(DrivingShortcut, value)


def create(
    session: Any,
    label: str = "Driver",
    value: int | float = 0.0,
    numeric_type: str = "REAL",
    dimension: str = "SCALAR",
) -> str:
    driver = DrivingShortcut(label, value, numeric_type, dimension)
    session.replace_document(driving_shortcuts=(*session.document.driving_shortcuts, driver))
    return driver.id


def install(session: Any, value: DrivingShortcut) -> None:
    from .property_writes import editable

    before = selected(session, value.id)
    for target in shortcut_ownership.targets(session.document, value):
        editable(session, target)
    changed = replace(value, generation=before.generation + int(evaluation_changed(before, value)))
    drivers = tuple(changed if d.id == value.id else d for d in session.document.driving_shortcuts)
    candidate = replace(session.document, driving_shortcuts=drivers)
    validate_writers(candidate)
    shortcut_operations.validate_policy(candidate, value)
    session.replace_document(driving_shortcuts=drivers)


def configure(session: Any, driver: str, changes: dict[str, Any]) -> None:
    if set(changes) - {"label", "numeric_type", "dimension", "value", "exposed", "policy"}:
        raise ValueError("Unknown driver setting; use driver.value or formula operations.")
    if "policy" in changes:
        changes = dict(changes, policy=shortcut_codec.policy(changes["policy"]))
    install(session, replace(selected(session, driver), **changes))


def evaluation_changed(before: DrivingShortcut, after: DrivingShortcut) -> bool:
    names = ("value", "numeric_type", "dimension", "formulas")
    return any(getattr(before, name) != getattr(after, name) for name in names)


def set_value(session: Any, driver: str, value: int | float) -> None:
    install(session, replace(selected(session, driver), value=value))


def remove(session: Any, driver: str) -> None:
    selected(session, driver)
    dependents = [
        d.label
        for d in session.document.driving_shortcuts
        if d.id != driver and any(i.driver == driver for f in d.formulas for i in f.inputs)
    ]
    if dependents:
        raise ValueError(
            "Resolve dependent formula inputs before removing: " + ", ".join(dependents)
        )
    session.replace_document(
        driving_shortcuts=tuple(d for d in session.document.driving_shortcuts if d.id != driver)
    )


def add_formula(
    session: Any,
    driver: str,
    target: dict[str, Any],
    expression: str,
    inputs: list[dict[str, Any]] | None = None,
    enabled: bool = True,
) -> str:
    record = shortcut_codec.formula(
        dict(target=target, expression=expression, inputs=inputs or (), enabled=enabled)
    )
    validate_formula(session, record)
    original = selected(session, driver)
    install(session, replace(original, formulas=(*original.formulas, record)))
    return record.id


def formula_record(session: Any, driver: str, formula: str) -> DrivingFormula:
    value = next((f for f in selected(session, driver).formulas if f.id == formula), None)
    if value is None:
        raise ValueError("Unknown driving formula.")
    return value


def update_formula(session: Any, driver: str, formula: str, changes: dict[str, Any]) -> None:
    if set(changes) - {"target", "expression", "inputs", "enabled"}:
        raise ValueError("Unknown formula setting.")
    record = shortcut_codec.formula(
        dict(asdict(formula_record(session, driver, formula)), **changes)
    )
    validate_formula(session, record)
    original = selected(session, driver)
    install(
        session,
        replace(
            original, formulas=tuple(record if f.id == formula else f for f in original.formulas)
        ),
    )


def remove_formula(session: Any, driver: str, formula: str) -> None:
    formula_record(session, driver, formula)
    original = selected(session, driver)
    install(
        session, replace(original, formulas=tuple(f for f in original.formulas if f.id != formula))
    )


def validate_formula(session: Any, formula: DrivingFormula) -> None:
    target = property_catalog.resolve(session.document, formula.target)
    if not target.writable:
        raise ValueError(target.reason or "Formula target is read-only.")
    for entry in formula.inputs:
        if entry.property is not None:
            descriptor = property_catalog.resolve(session.document, entry.property)
            if descriptor.components != 1 and entry.property.component is None:
                raise ValueError("Choose a numerical vector component for this formula input.")
        else:
            selected(session, entry.driver)


def inspect(session: Any, driver: str) -> dict[str, Any]:
    item = selected(session, driver)
    ids = {f.id for f in item.formulas}
    return dict(
        asdict(item),
        owners=sorted(shortcut_ownership.owners(session.document, item)),
        scp_owner=shortcut_ownership.scp_owner(session.document, item),
        results=[asdict(r) for r in session.document.formula_results if r.formula in ids],
    )
