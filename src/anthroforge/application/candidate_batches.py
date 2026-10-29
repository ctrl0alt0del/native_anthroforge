"""Candidate execution respects the same coherent formula batches as live scheduling."""

from typing import Any

from anthroforge.core.results import Port

from . import formula_batches, formula_tasks


def formulas(document: Any, pending: set[Port]) -> dict[Port, Any]:
    keys = {p.owner for p in pending if p.output == "formula"}
    result = {}
    for group in formula_batches.plan(document, keys) if keys else ():
        contract = formula_tasks.declaration(document, group)
        for key in group:
            result[Port(key, "formula")] = contract
    return result


def ready(document: Any, graph: Any, pending: set[Port]) -> list[Port]:
    batches = formulas(document, pending)
    return [
        p
        for p in pending
        if not ((batches[p].prerequisites if p in batches else graph.get(p, set())) & pending)
    ]


def group(document: Any, port: Port, pending: set[Port]) -> set[str]:
    contract = formulas(document, pending).get(port)
    return (
        {p.owner for p in contract.provides if p.output == "formula"} if contract else {port.owner}
    )
