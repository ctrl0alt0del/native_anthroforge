"""Accepted-result provenance shared by meshes, paths and future evaluated outputs."""

from typing import Any

from anthroforge.core.document import Document
from anthroforge.core.results import EvaluationResult, Port

from .construction_policy import revisions


def accepted_result(source: Document, item: Any, inputs: set[Port], key: str) -> EvaluationResult:
    pending = tuple(
        e.id
        for e in (*source.entities, *source.objects)
        if any(p.owner == e.id for p in inputs) and e.id != item.id and e.result.status == "pending"
    )
    return EvaluationResult(
        key,
        item.result.revision + 1,
        item.construction_revision,
        revisions(source, inputs),
        pending,
    )
