"""Retained imported geometry is displayable, but missing-input outputs are never current."""

from dataclasses import fields, replace
from typing import Any

from anthroforge.core.results import ControlResult, EvaluationResult, Port
from anthroforge.core.shortcuts import FormulaResult
from anthroforge.core.tissues import TissueVCP

from . import dependencies
from .assembly_provenance import results

MISSING = "Resolve imported references; displaying saved source geometry."
CHANGED = "Imported inputs changed; displaying saved source geometry until evaluated."
INCOMPLETE = "The saved source output was pending; showing its last accepted geometry."


def blocked(document: Any) -> set[Port]:
    missing = {r.id for r in document.external_references if not r.target}
    graph = dependencies.graph(document)
    seeds = {port for port in graph.consumers if port.owner in missing}
    return dependencies.closure(graph.consumers, seeds)


def mark(preparation: Any) -> None:
    from .assembly_formula_inputs import invalidate_changed

    document = preparation.candidate().merge(preparation.destination)
    invalidate_changed(preparation, document)
    affected = blocked(document)
    changed = changed_outputs(
        document, preparation.mapping.changed, preparation.mapping.changed_ports
    )
    mark_values(preparation.values, affected, changed)


def mark_values(values: Any, affected: set[Port], changed: set[Port]) -> None:
    for group in ("entities", "objects", "controls"):
        values[group] = tuple(
            retained(retained(completed_snapshot(item), changed, CHANGED), affected)
            for item in values[group]
        )
    values["formula_results"] = tuple(
        formula(r, affected, changed) for r in values.get("formula_results", ())
    )


def completed_snapshot(item: Any) -> Any:
    changes = {
        name: replace(value, status="invalid", error=INCOMPLETE)
        for name, value in results(item)
        if value.status == "pending"
    }
    return replace(item, **changes)


def retained(item: Any, affected: set[Port], message: str = MISSING) -> Any:
    outputs = {p.output for p in affected if p.owner == item.id}
    if not outputs:
        return item
    changes = {}
    for field in fields(item):
        value = getattr(item, field.name)
        if isinstance(value, (EvaluationResult, ControlResult)) and affected_result(
            item, field.name, outputs
        ):
            changes[field.name] = replace(
                value, status="pending" if message == CHANGED else "invalid", error=message
            )
    return replace(item, **changes)


def formula(value: FormulaResult, missing: set[Port], changed: set[Port]) -> FormulaResult:
    port = Port(value.formula, "formula")
    message = MISSING if port in missing else CHANGED if port in changed else ""
    if message:
        return replace(value, status="pending" if message == CHANGED else "invalid", error=message)
    if value.status == "pending":
        return replace(value, status="invalid", error=INCOMPLETE)
    return value


def affected_result(item: Any, field: str, outputs: set[str]) -> bool:
    if isinstance(item, TissueVCP):
        phase = "final" if field == "result" else field.removesuffix("_result")
        return phase in outputs
    return bool(outputs & {"path", "binding", "geometry", "cage", "control"})


def changed_outputs(document: Any, owners: set[str], ports: set[Port] | None = None) -> set[Port]:
    graph = dependencies.graph(document)
    seeds = {port for port in graph if port.owner in owners and port.output != "pose"}
    return dependencies.closure(graph.consumers, seeds | (ports or set()))


def schedule(session: Any, candidate: Any) -> list[str]:
    from . import output_tasks

    outputs = changed_outputs(session.document, set(), changed_ports(candidate)) - blocked(
        session.document
    )
    before = {job.id for job in session.scheduler.jobs}
    output_tasks.schedule_outputs(session, outputs, released=True)
    return [job.id for job in session.scheduler.jobs if job.id not in before]


def changed_ports(candidate: Any) -> set[Port]:
    rows = (
        v
        for group in ("entities", "objects", "controls")
        for v in candidate.additions.get(group, ())
    )
    ports = {
        result_port(v, name) for v in rows for name, result in results(v) if result.error == CHANGED
    }
    return ports | {
        Port(r.formula, "formula")
        for r in candidate.additions.get("formula_results", ())
        if r.error == CHANGED
    }


def result_port(item: Any, field: str) -> Port:
    from anthroforge.core.object_outputs import output

    if isinstance(item, TissueVCP):
        return Port(item.id, "final" if field == "result" else field.removesuffix("_result"))
    return Port(item.id, output(item))
