"""Retained imported geometry is displayable, but missing-input outputs are never current."""

from dataclasses import fields, replace
from typing import Any

from anthroforge.core.results import EvaluationResult, Port
from anthroforge.core.tissues import TissueVCP

from . import dependencies


def blocked(document: Any) -> set[Port]:
    missing = {r.id for r in document.external_references if not r.target}
    graph = dependencies.graph(document)
    seeds = {port for port in graph.consumers if port.owner in missing}
    return dependencies.closure(graph.consumers, seeds)


def mark(preparation: Any) -> None:
    document = preparation.candidate().merge(preparation.destination)
    affected = blocked(document)
    for group in ("entities", "objects", "controls"):
        preparation.values[group] = tuple(
            retained(item, affected) for item in preparation.values[group]
        )


def retained(item: Any, affected: set[Port]) -> Any:
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
                error="Resolve imported references; displaying saved source geometry.",
            )
    return replace(item, **changes)


def affected_result(item: Any, field: str, outputs: set[str]) -> bool:
    if isinstance(item, TissueVCP):
        phase = "final" if field == "result" else field.removesuffix("_result")
        return phase in outputs or "geometry" in outputs
    return bool(outputs & {"path", "binding", "geometry", "cage", "control"})
