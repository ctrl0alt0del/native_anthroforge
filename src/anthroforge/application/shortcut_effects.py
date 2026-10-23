"""Read-only output influence over the authoritative dependency graph."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.formula_dependencies import effects as property_effects
from anthroforge.core.formula_dependencies import property_port
from anthroforge.core.results import Port
from anthroforge.core.shortcuts import Shortcut

from . import dependencies, shortcut_operations, shortcut_ownership
from .construction_policy import mode
from .dependency_inspection import cycle_records, port_record
from .workspace_policy import included


def selected(session: Any, shortcut: str) -> Any:
    value = next(
        (s for s in shortcut_operations.ordered(session.document) if s.id == shortcut), None
    )
    if value is None:
        raise ValueError("Unknown shortcut identity.")
    return value


def direct(value: Any) -> tuple[Any, ...]:
    return (
        (value.reference,)
        if isinstance(value, Shortcut)
        else tuple(f.target for f in value.formulas if f.enabled)
    )


def ports(document: Any, value: Any) -> frozenset[Port]:
    graph = dependencies.graph(document)
    seeds = {Port(value.id, "driver")} if not isinstance(value, Shortcut) else set()
    for reference in direct(value):
        seeds.add(property_port(reference))
        seeds.update(property_effects(document.registry.records.get(reference.target), reference))
    return frozenset(dependencies.closure(graph.consumers, seeds))


def affected(session: Any, value: Any) -> frozenset[Port]:
    service = session.shortcut_observation
    graph = dependencies.graph(session.document)
    stamp = (graph, value)
    previous = service.effects.get(value.id)
    if previous is None or previous[0] != stamp:
        service.effects[value.id] = (stamp, ports(session.document, value))
    return frozenset(service.effects[value.id][1])


def readiness(document: Any, port: Port) -> dict[str, Any]:
    result = document.formula_index.results.get(port.owner)
    item = document.registry.records.get(port.owner)
    if item is not None:
        result = output_result(item, port.output)
    return dict(
        status=output_status(item, result, port.output),
        error=getattr(result, "error", ""),
        pending=list(getattr(result, "pending", ())),
        revision=getattr(result, "revision", None),
    )


def output_status(item: Any, result: Any, output: str) -> str:
    state = getattr(item, "status", "ready")
    if output in ("pose", "control") and state in ("edited", "stale", "failed"):
        return "failed" if state == "failed" else "pending"
    return str(getattr(result, "status", "ready"))


def output_result(item: Any, output: str) -> Any:
    return getattr(item, output + "_result", getattr(item, "result", None))


def row(session: Any, port: Port, targets: set[str], published: set[Port]) -> dict[str, Any]:
    document = session.document
    item = document.registry.records.get(port.owner)
    return dict(
        port_record(document, port),
        **readiness(document, port),
        direct=port.owner in targets,
        published=port in published,
        editable=included(document, session.workspace, port.owner) if item else False,
        update_mode=mode(document, port.owner) if item else "LIVE",
        **cycle_records(document, port),
    )


def inspect(
    session: Any, shortcut: str, search: str = "", offset: int = 0, limit: int = 100
) -> dict[str, Any]:
    if offset < 0 or not 1 <= limit <= 500:
        raise ValueError("Inspection requires a nonnegative offset and limit 1..500.")
    value = selected(session, shortcut)
    rows = effect_rows(session, value, search)
    return dict(
        revision=session.document.revision,
        shortcut=shortcut,
        total=len(rows),
        rows=rows[offset : offset + limit],
        targets=[asdict(r) for r in direct(value)],
        owners=sorted(shortcut_ownership.owners(session.document, value)),
    )


def effect_rows(session: Any, value: Any, search: str = "") -> list[dict[str, Any]]:
    targets = {r.target for r in direct(value)}
    observed = session.shortcut_observation.latest.get(value.id)
    published = observed.published if observed else set()
    rows = [
        row(session, p, targets, published)
        for p in sorted(affected(session, value), key=lambda p: (p.owner, p.output))
    ]
    return [r for r in rows if search.casefold() in (r["name"] + " " + r["output"]).casefold()]
