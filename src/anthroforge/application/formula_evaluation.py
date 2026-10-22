"""Owned formula evaluation: native arithmetic, graph orchestration and coherent candidates."""

from dataclasses import dataclass, field
from typing import Any

from anthroforge.core.results import Port
from anthroforge.native import expressions

from . import dependencies, formula_candidates, formula_inputs


@dataclass
class Evaluation:
    context: formula_inputs.Captured
    selected: set[str]
    values: dict[str, Any] = field(default_factory=dict)
    failures: dict[str, str] = field(default_factory=dict)
    candidates: list[Any] = field(default_factory=list)


def evaluate(context: Any, ids: set[str], cancel: Any) -> Evaluation:
    result = Evaluation(context, ids)
    graph = dependencies.graph(context.document)
    for key in ids:
        if Port(key, "formula") in graph.blocked:
            result.failures[key] = "Cyclic or missing formula dependency; accepted values retained."
    execute(result, cancel)
    validate(result)
    return result


def execute(result: Evaluation, cancel: Any) -> None:
    records = formula_inputs.formulas(result.context.document)
    pending = {key for key in result.selected if key in records} - result.failures.keys()
    while pending:
        ready = ready_formulas(result, records, pending)
        if not ready:
            raise ValueError("Formula dependency order is unresolved.")
        for key in ready:
            if cancel.is_set():
                raise RuntimeError("Formula evaluation cancelled.")
            driver, formula = records[key]
            compute(result, driver, formula, cancel)
        pending.difference_update(ready)


def compute(result: Evaluation, driver: Any, formula: Any, cancel: Any) -> None:
    context = result.context
    try:
        require_inputs(result, formula)
        symbols = formula_inputs.symbols(context, driver, formula)
        program = expressions.compile(context.engine, formula.expression, symbols, cancel.handle)
        value = program.evaluate(
            formula_inputs.values(context, driver, formula, result.values), cancel.handle
        )
        result.values[formula.id] = formula_inputs.target_value(context, formula, program, value)
    except (ValueError, RuntimeError, StopIteration, OverflowError) as error:
        result.failures[formula.id] = str(error) or "Missing formula input."


def ready_formulas(result: Evaluation, records: Any, pending: set[str]) -> list[str]:
    return sorted(
        key
        for key in pending
        if not formula_inputs.dependencies(result.context.document, records[key][1]) & pending
    )


def require_inputs(result: Evaluation, formula: Any) -> None:
    upstream = formula_inputs.dependencies(result.context.document, formula)
    if upstream & result.failures.keys():
        raise ValueError("A prerequisite formula failed; accepted value retained.")
    previous = {r.formula: r for r in result.context.document.formula_results}
    if any(
        key not in result.selected and key in previous and previous[key].status == "failed"
        for key in upstream
    ):
        raise ValueError("A prerequisite formula failed; accepted value retained.")


def propagate_failures(result: Evaluation) -> None:
    graph = dependencies.graph(result.context.document)
    blocked = dependencies.closure(
        graph.consumers, {Port(key, "formula") for key in result.failures}
    )
    for port in blocked:
        if port.output == "formula" and port.owner in result.selected:
            result.failures.setdefault(
                port.owner, "A prerequisite formula failed; accepted value retained."
            )
    for key in result.failures:
        result.values.pop(key, None)


def validate(result: Evaluation) -> None:
    result.failures.update(formula_candidates.rejected(result.context, result.values))
    while True:
        propagate_failures(result)
        result.candidates, rejected = formula_candidates.prepare(result.context, result.values)
        if not rejected:
            return
        result.failures.update(rejected)
