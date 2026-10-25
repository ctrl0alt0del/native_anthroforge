"""Accepted multi-stage bundles invalidate consumers without rebuilding their own stages."""

from collections import defaultdict
from dataclasses import replace
from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.points import Anchor
from anthroforge.core.results import Port
from anthroforge.core.tissue_revisions import PHASES
from anthroforge.core.tissues import TissueVCP

from . import control_tasks, dependencies, geometry_outputs, output_tasks, tissue_results


def changed(session: Any, prepared: set[Port], authored: set[Port]) -> None:
    graph = dependencies.reverse(dependencies.graph(session.document))
    affected = dependencies.closure(graph, prepared | authored) - prepared
    mark_pending(session, affected)
    control_tasks.edited(session, prepared | authored)
    output_tasks.schedule(session, {p.owner for p in affected})
    geometry = {p.owner for p in affected if p.output == "geometry"}
    from .construction_tasks import schedule

    schedule(session, geometry)


def mark_pending(session: Any, ports: set[Port]) -> None:
    groups: dict[str, set[str]] = defaultdict(set)
    for port in ports:
        groups[port.owner].add(port.output)
    changes = {}
    for name in ("entities", "objects"):
        records = getattr(session.document, name)
        updated = tuple(pending(item, groups.get(item.id, set())) for item in records)
        if updated != records:
            changes[name] = updated
    if changes:
        session.replace_document(**changes)


def pending(item: Any, outputs: set[str]) -> Any:
    if isinstance(item, TissueVCP):
        phases = outputs & set(PHASES)
        return tissue_results.pending(item, phases) if phases else item
    if isinstance(item, (Curve, Anchor)) and outputs & {"path", "binding"}:
        return replace(item, result=replace(item.result, status="pending"))
    return geometry_outputs.pending_record(item, {item.id} if "geometry" in outputs else set())
