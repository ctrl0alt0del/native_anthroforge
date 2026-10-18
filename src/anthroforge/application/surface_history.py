"""Retroactive authored publication retains only geometry valid for that snapshot's inputs."""

from dataclasses import replace
from typing import Any

from anthroforge.core.results import EvaluationResult, Port
from anthroforge.core.surfaces import Surface

from . import authored_jobs
from .construction_policy import revisions


def merge(document: Any, ready: Surface, original: Surface, existing: bool) -> Any:
    if any(use.curve not in document.registry.records for use in original.curves):
        return document
    item = ready if matches(document, ready) else pending(document, original, existing)
    if not existing:
        return authored_jobs.append_object(document, item)
    objects = tuple(item if o.id == item.id else o for o in document.objects)
    return replace(document, objects=objects)


def matches(document: Any, item: Surface) -> bool:
    inputs = {Port(value.owner, value.output) for value in item.result.inputs}
    if any(p.owner not in document.registry.records for p in inputs):
        return False
    return revisions(document, inputs) == item.result.inputs


def pending(document: Any, item: Surface, existing: bool) -> Surface:
    previous = document.registry.records.get(item.id) if existing else None
    result = (
        replace(previous.result, status="pending")
        if previous
        else EvaluationResult(status="pending")
    )
    return replace(item, result=result)
