"""Coherent invariant groups: no execution-order winner for conflicting properties."""

from typing import Any

from anthroforge.core.numeric_properties import read_path

from . import formula_inputs, property_writes


def group(context: Any, reference: Any) -> tuple[Any, ...]:
    parent = (
        read_path(context.document.object(reference.target), reference.path[:-1])
        if reference.path[0] != "transform"
        else None
    )
    field = reference.path[-1]
    if type(parent).__name__ == "TissueInflation" and field in ("minimum", "amount"):
        field = "thickness_limits"
    return reference.target, reference.path[:-1], field


def grouped(context: Any, outputs: dict[str, Any]) -> dict[Any, list[Any]]:
    records = formula_inputs.formulas(context.document)
    groups: dict[Any, list[Any]] = {}
    for key, value in outputs.items():
        reference = records[key][1].target
        groups.setdefault(group(context, reference), []).append((key, reference, value))
    return groups


def rejected(context: Any, outputs: dict[str, Any]) -> dict[str, str]:
    failures: dict[str, str] = {}
    for rows in grouped(context, outputs).values():
        try:
            property_writes.prepare(context, rows[0][1].target, tuple((r, v) for _, r, v in rows))
        except (ValueError, RuntimeError) as error:
            failures.update((key, str(error)) for key, _, _ in rows)
    return failures


def prepare(context: Any, outputs: dict[str, Any]) -> tuple[list[Any], dict[str, str]]:
    groups: dict[str, list[Any]] = {}
    for key, (_, formula) in formula_inputs.formulas(context.document).items():
        if key in outputs:
            groups.setdefault(formula.target.target, []).append((key, formula.target, outputs[key]))
    candidates: list[Any] = []
    failures: dict[str, str] = {}
    for target, rows in groups.items():
        try:
            candidates.append(
                property_writes.prepare(context, target, tuple((r, v) for _, r, v in rows))
            )
        except (ValueError, RuntimeError) as error:
            failures.update((key, str(error)) for key, _, _ in rows)
    return candidates, failures
