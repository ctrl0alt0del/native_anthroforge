"""Production expression evaluation and reviewed formula authority inside owned state."""

from dataclasses import replace
from typing import Any

from anthroforge.core.entities import SCP
from anthroforge.core.results import Port
from anthroforge.core.shortcuts import FormulaResult
from anthroforge.core.skeleton_update import Finding

from . import (
    entity_revisions,
    formula_evaluation,
    formula_inputs,
    formula_tasks,
    object_revisions,
    property_operations,
)


def evaluate(context: Any, keys: set[str], review: bool = False) -> None:
    captured = formula_inputs.Captured(context.document, context.resources, context.engine)
    result = formula_evaluation.evaluate(captured, keys, context.cancel)
    if review and not allowed(context, result):
        return
    for before, after in result.candidates:
        revision = (
            entity_revisions.authored if isinstance(before, SCP) else object_revisions.authored
        )
        context.install(revision(before, after) if before != after else before)
    accept(context, result)


def allowed(context: Any, result: Any) -> bool:
    valid = True
    for key, value in result.values.items():
        formula = formula_inputs.formulas(context.document)[key][1]
        current = property_operations.read(result.context, formula.target)
        if current == value:
            continue
        valid &= review_value(context, key, formula.target.target, current, value)
    return valid


def review_value(context: Any, key: str, owner: str, current: Any, value: Any) -> bool:
    chosen = key in context.options.get("use_formula_values", ())
    message = f"Formula would replace {current} with {value}; choose formula value or disable it."
    context.findings.append(
        Finding(
            "driver_value:" + key,
            owner,
            message,
            blocking=not chosen,
            acknowledge=chosen,
            kind="property",
        )
    )
    return chosen


def accept(context: Any, result: Any) -> None:
    records = {r.formula: r for r in context.document.formula_results}
    for key in result.selected:
        records[key] = formula_tasks.accepted_result(
            result, key, records.get(key, FormulaResult(key))
        )
        port = Port(key, "formula")
        context.prepared.add(port)
        if key in result.failures:
            context.failed.add(port)
            context.findings.append(
                Finding("failure:" + key, key, result.failures[key], blocking=True, kind="property")
            )
    context.document = replace(context.document, formula_results=tuple(records.values()))


def handler(context: Any, port: Port) -> None:
    evaluate(context, {port.owner})
