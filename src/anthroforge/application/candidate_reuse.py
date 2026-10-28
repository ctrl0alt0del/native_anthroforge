"""Reuse saved numerical outputs only after proving their inputs are still equivalent."""

from dataclasses import replace
from typing import Any

from anthroforge.core import graph_records, snapshot_definitions
from anthroforge.core.entities import SCP
from anthroforge.core.object_outputs import output
from anthroforge.core.results import Port, geometry_asset

from . import construction_policy, dependencies, evaluation_results


def configure(context: Any, preparation: Any) -> None:
    context.reuse = {}
    p = preparation
    for original in p.selection.records.values():
        result = getattr(original, "result", None)
        if result is None or result.status != "ready" or getattr(result, "pending", ()):
            continue
        port = Port(original.id, output(original))
        if source_current(p.source.document, port, result):
            context.reuse[Port(p.ids[original.id], port.output)] = (p, original, port)


def source_current(document: Any, port: Port, result: Any) -> bool:
    if not getattr(result, "asset", "") or result.error:
        return False
    if result.authored_revision != document.object(port.owner).construction_revision:
        return False
    for read in result.inputs:
        current = construction_policy.revision(document, Port(read.owner, read.output))
        if (read.owner, read.output) == (port.owner, port.output):
            current = replace(current, accepted=read.accepted)
        if current != read:
            return False
    return True


def install(context: Any, port: Port) -> bool:
    proof = context.reuse.get(port)
    if proof is None:
        return False
    p, original, source_port = proof
    reads = dependencies.ports(p.source.document, source_port)
    if not all(equivalent(context, p, read) for read in reads):
        return False
    item = context.document.object(port.owner)
    inputs = dependencies.ports(context.document, port)
    result = evaluation_results.accepted_result(context.document, item, inputs, item.result.asset)
    context.install(replace(item, result=result))
    return True


def equivalent(context: Any, p: Any, port: Port) -> bool:
    if port.owner not in p.selection.records:
        return False
    original = p.source.document.object(port.owner)
    expected = graph_records.rewritten(original, p.ids, p.assets)
    current = context.document.object(p.ids[port.owner])
    if isinstance(original, SCP):
        return scp_equivalent(expected, current, port.output)
    return snapshot_definitions.same(expected, current)


def scp_equivalent(expected: Any, current: Any, kind: str) -> bool:
    names = (
        ("matrix", "geometry_offset") if kind == "pose" else ("primitive", "deformers", "thickness")
    )
    return all(getattr(expected, n) == getattr(current, n) for n in names) and (
        kind == "pose" or geometry_asset(expected) == geometry_asset(current)
    )
