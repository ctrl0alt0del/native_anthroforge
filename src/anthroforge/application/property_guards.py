"""Active formula writers reserve components across all authored mutation paths."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from anthroforge.core.numeric_properties import PropertyRef, overlaps


def driven(document: Any, reference: PropertyRef) -> str:
    return next(
        (
            f.id
            for d in document.driving_shortcuts
            for f in d.formulas
            if f.enabled and overlaps(f.target, reference)
        ),
        "",
    )


def validate_writers(document: Any) -> None:
    formulas = [f for d in document.driving_shortcuts for f in d.formulas if f.enabled]
    for index, formula in enumerate(formulas):
        if any(overlaps(formula.target, other.target) for other in formulas[:index]):
            raise ValueError("Only one active formula may write each numerical component.")


def require_changes(session: Any, before: Any, after: Any) -> None:
    require_references(session, before, after)
    for label, formula in retained_writers(before, after):
        if formula.id not in session.formula_write_authority:
            if changed(session, before, after, formula.target):
                raise ValueError(
                    f"This property is driven by {label}; disable its formula to edit it."
                )


def retained_writers(before: Any, after: Any) -> Iterator[tuple[str, Any]]:
    previous = {f.id: f for d in before.driving_shortcuts for f in d.formulas if f.enabled}
    for driver in after.driving_shortcuts:
        for formula in driver.formulas:
            old = previous.get(formula.id)
            if formula.enabled and old is not None and formula.target == old.target:
                yield driver.label, formula


def require_references(session: Any, before: Any, after: Any) -> None:
    for driver in after.driving_shortcuts:
        for formula in driver.formulas:
            references = (formula.target, *(i.property for i in formula.inputs if i.property))
            for ref in references:
                require_reference(session, before, after, ref, driver.label)


def require_reference(session: Any, before: Any, after: Any, ref: PropertyRef, label: str) -> None:
    from .property_operations import read

    previous = before.registry.records.get(ref.target)
    current = after.registry.records.get(ref.target)
    if previous is None or previous is current:
        return
    require_address(previous, current, ref)
    try:
        if current is None:
            raise ValueError("Removed object.")
        read(session, ref, current)
    except (ValueError, AttributeError):
        missing_reference(label)


def require_address(previous: Any, current: Any, ref: PropertyRef) -> None:
    from anthroforge.core.construction import Control

    if (
        isinstance(previous, Control)
        and isinstance(current, Control)
        and previous.resolution != current.resolution
        and ref.path[0] in ("points", "weights")
    ):
        raise ValueError(
            "Resolve formula references to cage points/weights before resizing the lattice."
        )


def missing_reference(label: str) -> None:
    raise ValueError(
        "Resolve driving shortcut references before removing this property: " + label
    ) from None


def changed(session: Any, before: Any, after: Any, reference: PropertyRef) -> bool:
    from .property_operations import read
    from .property_transforms import equivalent

    previous = before.registry.records.get(reference.target)
    current = after.registry.records.get(reference.target)
    if previous is None or current is None or previous is current:
        return False
    old, new = read(session, reference, previous), read(session, reference, current)
    return not equivalent(old, new) if reference.path[0] == "transform" else bool(old != new)


@contextmanager
def publication(session: Any, formulas: set[str]) -> Iterator[None]:
    previous = session.formula_write_authority
    session.formula_write_authority = frozenset(formulas)
    try:
        yield
    finally:
        session.formula_write_authority = previous
