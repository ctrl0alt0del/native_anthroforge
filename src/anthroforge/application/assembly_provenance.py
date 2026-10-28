"""Retained result evidence and input identities are separate from authored graph copying."""

from dataclasses import fields, replace
from typing import Any

from anthroforge.core import graph_records
from anthroforge.core.assembly import RetainedOutput
from anthroforge.core.results import ControlResult, EvaluationResult, Port
from anthroforge.core.shortcuts import FormulaResult

from . import construction_policy

RESULTS = (ControlResult, EvaluationResult, FormulaResult)


def outputs(values: Any) -> tuple[RetainedOutput, ...]:
    return tuple(
        snapshot(item, name, value)
        for rows in values.values()
        for item in rows
        for name, value in results(item)
    )


def results(item: Any) -> list[tuple[str, Any]]:
    if isinstance(item, FormulaResult):
        return [("", item)]
    return [
        (f.name, getattr(item, f.name))
        for f in fields(item)
        if isinstance(getattr(item, f.name), RESULTS)
    ]


def snapshot(item: Any, name: str, value: Any) -> RetainedOutput:
    return RetainedOutput(
        getattr(item, "id", getattr(item, "formula", "")),
        name,
        getattr(value, "asset", ""),
        value.revision,
        getattr(item, "generation", 0),
        value.status,
        value.error,
    )


def restore(document: Any, item: Any) -> Any:
    snapshots = {(r.owner, r.field): r for p in document.imports for r in p.outputs}
    changes = {}
    for name, value in results(item):
        previous = snapshots.get((getattr(item, "id", getattr(item, "formula", "")), name))
        if previous and restorable(previous, item, value):
            updated = replace(value, status=previous.status, error=previous.error)
            if not name:
                return updated
            changes[name] = updated
    return replace(item, **changes)


def restorable(previous: Any, item: Any, value: Any) -> bool:
    from .assembly_result_state import MISSING

    return bool(
        value.error == MISSING
        and previous.asset == getattr(value, "asset", "")
        and previous.revision == value.revision
        and previous.generation == getattr(item, "generation", 0)
    )


def rewrite(preparation: Any) -> None:
    destination = preparation.candidate().merge(preparation.destination)
    reverse = {value: key for key, value in preparation.ids.items()}
    for group, rows in preparation.values.items():
        preparation.values[group] = tuple(
            rewrite_record(preparation, destination, item, reverse) for item in rows
        )


def rewrite_record(p: Any, document: Any, item: Any, reverse: Any) -> Any:
    owner = reverse.get(getattr(item, "id", ""), "")
    if isinstance(item, FormulaResult):
        pair = p.source.document.formula_index.formulas.get(reverse.get(item.formula, item.formula))
        owner = pair[0].id if pair else ""
    targets = external_targets(p, owner)
    changes = {}
    for name, value in results(item):
        inputs = tuple(rewrite_input(p, document, r, targets, reverse) for r in value.inputs)
        updated = replace(value, inputs=inputs)
        if not name:
            return updated
        changes[name] = updated
    return replace(item, **changes)


def external_targets(p: Any, owner: str) -> dict[str, str]:
    return {ref.target: target for ref, _, target in p.mapping.replacements.get(owner, ())}


def rewrite_input(p: Any, document: Any, value: Any, targets: Any, reverse: Any) -> Any:
    target = targets.get(value.owner, value.owner)
    updated = replace(value, owner=target)
    original = graph_records.rewritten(value, reverse)
    try:
        old = construction_policy.revision(p.source.document, Port(original.owner, original.output))
        current = construction_policy.revision(document, Port(target, value.output))
    except (ValueError, KeyError):
        return updated
    return current if old == original and equivalent_membership(updated, current) else updated


def equivalent_membership(previous: Any, current: Any) -> bool:
    return bool(previous.membership == current.membership or previous.output == "mirror")
