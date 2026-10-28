"""Retained imported geometry is displayable, but missing-input outputs are never current."""

from dataclasses import fields, replace
from typing import Any

from anthroforge.core.results import EvaluationResult, Port
from anthroforge.core.tissues import TissueVCP

from . import dependencies

MISSING = "Resolve imported references; displaying saved source geometry."
CHANGED = "Imported inputs changed; displaying saved source geometry until evaluated."


def blocked(document: Any) -> set[Port]:
    missing = {r.id for r in document.external_references if not r.target}
    graph = dependencies.graph(document)
    seeds = {port for port in graph.consumers if port.owner in missing}
    return dependencies.closure(graph.consumers, seeds)


def mark(preparation: Any) -> None:
    document = preparation.candidate().merge(preparation.destination)
    affected = blocked(document)
    changed = changed_outputs(document, preparation.mapping.changed)
    for group in ("entities", "objects", "controls"):
        preparation.values[group] = tuple(
            retained(retained(item, changed, CHANGED), affected)
            for item in preparation.values[group]
        )


def retained(item: Any, affected: set[Port], message: str = MISSING) -> Any:
    outputs = {p.output for p in affected if p.owner == item.id}
    if not outputs:
        return item
    changes = {}
    for field in fields(item):
        value = getattr(item, field.name)
        if isinstance(value, EvaluationResult) and affected_result(item, field.name, outputs):
            changes[field.name] = replace(
                value,
                status="invalid",
                error=message,
            )
    return replace(item, **changes)


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
    output_tasks.schedule_outputs(session, outputs)
    return [job.id for job in session.scheduler.jobs if job.id not in before]


def changed_owners(candidate: Any) -> set[str]:
    rows = (
        v
        for group in ("entities", "objects", "controls")
        for v in candidate.additions.get(group, ())
    )
    return {
        v.id
        for v in rows
        if any(
            isinstance(getattr(v, f.name), EvaluationResult) and getattr(v, f.name).error == CHANGED
            for f in fields(v)
        )
    }
