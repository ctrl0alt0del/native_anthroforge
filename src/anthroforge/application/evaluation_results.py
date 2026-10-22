"""Accepted-result provenance shared by meshes, paths and future evaluated outputs."""

from typing import Any

from anthroforge.core.document import Document
from anthroforge.core.results import EvaluationResult, Port

from .construction_policy import revisions


def matches(source: Document, result: EvaluationResult) -> bool:
    ports = {Port(value.owner, value.output) for value in result.inputs}
    try:
        return revisions(source, ports) == result.inputs
    except ValueError:
        return False


def accepted_result(source: Document, item: Any, inputs: set[Port], key: str) -> EvaluationResult:
    owners = {port.owner for port in inputs}
    pending = tuple(
        e.id
        for e in (*source.entities, *source.objects)
        if e.id in owners and e.id != item.id and e.result.status == "pending"
    )
    return EvaluationResult(
        key,
        item.result.revision + 1,
        item.construction_revision,
        revisions(source, inputs),
        pending,
    )
