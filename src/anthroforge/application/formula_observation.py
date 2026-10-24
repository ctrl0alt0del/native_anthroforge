"""Targeted invalidation from authored inputs and accepted property/pose publications."""

from dataclasses import replace
from typing import Any

from anthroforge.core.results import Port
from anthroforge.core.shortcuts import FormulaResult

from . import dependencies, formula_inputs


def source(document: Any, key: str) -> Any:
    from .construction_policy import revisions

    record = formula_inputs.formulas(document).get(key)
    if record is None:
        return None
    driver, formula = record
    ports = dependencies.ports(document, Port(key, "formula")) - {Port(key, "formula")}
    return driver.value, driver.numeric_type, driver.dimension, formula, revisions(document, ports)


def changed(session: Any, before: Any, exclude: frozenset[str] = frozenset()) -> None:
    if (
        not session.document.driving_shortcuts
        or session.formula_write_authority
        or session.formula_observing
    ):
        return
    dirty = {
        key
        for key in session.formula_invalidation.candidates(before, session.document) - exclude
        if source(before, key) != source(session.document, key)
    }
    if dirty:
        invalidate(session, dirty)


def invalidate(session: Any, dirty: set[str]) -> None:
    from .formula_tasks import pending

    session.formula_observing = True
    try:
        mark(session, dirty)
        pending(session)
    finally:
        session.formula_observing = False


def mark(session: Any, dirty: set[str]) -> None:
    graph = dependencies.graph(session.document)
    ports = dependencies.closure(graph.consumers, {Port(key, "formula") for key in dirty})
    affected = {p.owner for p in ports if p.output == "formula"}
    records = {r.formula: r for r in session.document.formula_results}
    for key in affected:
        records[key] = replace(records.get(key, FormulaResult(key)), status="pending", error="")
    session.scheduler.invalidate_ports(
        {Port(key, "formula") for key in affected}, reason="formula_input_changed"
    )
    session.replace_document(formula_results=tuple(records.values()))


def pending_upstream(document: Any, key: str, selected: set[str]) -> tuple[str, ...]:
    ports = formula_inputs.observations(document, {key})
    records = {r.formula: r for r in document.formula_results}
    formulas = {p.owner for p in ports if p.output == "formula"} - selected
    pending = {key for key in formulas if key in records and records[key].status == "pending"}
    for port in ports:
        item = document.registry.records.get(port.owner)
        if (
            item
            and port.output in ("path", "geometry", "final", "intrinsic", "pose")
            and item.result.status == "pending"
        ):
            pending.add(item.id)
    return tuple(sorted(pending))
