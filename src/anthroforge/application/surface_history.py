"""Retroactive authored publication retains only geometry valid for that snapshot's inputs."""

from dataclasses import replace
from typing import Any

from anthroforge.core.results import EvaluationResult
from anthroforge.core.surfaces import Surface

from . import authored_jobs
from .evaluation_results import matches


def merge(document: Any, ready: Surface, original: Surface, existing: bool) -> Any:
    if any(use.curve not in document.registry.records for use in original.curves):
        return document
    item = ready if matches(document, ready.result) else pending(document, original, existing)
    if not existing:
        return authored_jobs.append_object(document, item)
    objects = tuple(item if o.id == item.id else o for o in document.objects)
    return replace(document, objects=objects)


def pending(document: Any, item: Surface, existing: bool) -> Surface:
    previous = document.registry.records.get(item.id) if existing else None
    result = (
        replace(previous.result, status="pending")
        if previous
        else EvaluationResult(status="pending")
    )
    return replace(item, result=result)
