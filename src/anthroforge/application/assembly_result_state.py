"""Retained imported geometry is displayable, but missing-input outputs are never current."""

from dataclasses import fields, replace
from typing import Any

from anthroforge.core.results import ControlResult, EvaluationResult, Port
from anthroforge.core.shortcuts import FormulaResult
from anthroforge.core.tissues import TissueVCP

from . import dependencies

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
    changed = changed_outputs(document, preparation.mapping.changed)
    for group in ("entities", "objects", "controls"):
        preparation.values[group] = tuple(
            retained(retained(completed_snapshot(item), changed, CHANGED), affected)
            for item in preparation.values[group]
        )
    preparation.values["formula_results"] = tuple(
        formula(r, affected, changed) for r in preparation.values.get("formula_results", ())
    )


def completed_snapshot(item: Any) -> Any:
    from .assembly_provenance import results

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
            changes[field.name] = replace(value, status="invalid", error=message)
    return replace(item, **changes)


def formula(value: FormulaResult, missing: set[Port], changed: set[Port]) -> FormulaResult:
    port = Port(value.formula, "formula")
    message = MISSING if port in missing else CHANGED if port in changed else ""
    if message:
        return replace(value, status="invalid", error=message)
    if value.status == "pending":
        return replace(value, status="invalid", error=INCOMPLETE)
    return value


def affected_result(item: Any, field: str, outputs: set[str]) -> bool:
    if isinstance(item, TissueVCP):
        phase = "final" if field == "result" else field.removesuffix("_result")
        return phase in outputs or "geometry" in outputs
    return bool(outputs & {"path", "binding", "geometry", "cage", "control"})


def changed_outputs(document: Any, owners: set[str]) -> set[Port]:
    graph = dependencies.graph(document)
    seeds = {port for port in graph if port.owner in owners and port.output != "pose"}
    return dependencies.closure(graph.consumers, seeds)


def schedule(session: Any, candidate: Any) -> list[str]:
    from . import output_tasks

    owners = changed_owners(candidate)
    outputs = changed_outputs(session.document, owners) - blocked(session.document)
    before = {job.id for job in session.scheduler.jobs}
    output_tasks.schedule_outputs(session, outputs, released=True)
    return [job.id for job in session.scheduler.jobs if job.id not in before]


def changed_owners(candidate: Any) -> set[str]:
    rows = (
        v
        for group in ("entities", "objects", "controls")
        for v in candidate.additions.get(group, ())
    )
    owners = {v.id for v in rows if changed(v)}
    return owners | {
        r.formula for r in candidate.additions.get("formula_results", ()) if r.error == CHANGED
    }


def changed(item: Any) -> bool:
    from .assembly_provenance import results

    return any(value.error == CHANGED for _, value in results(item))
