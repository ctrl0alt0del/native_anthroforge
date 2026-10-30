"""Shared explicit evaluation request, independent of command dispatch."""

from typing import TYPE_CHECKING

from . import construction_tasks, evaluation, output_tasks

if TYPE_CHECKING:
    from .session import Session


def evaluate(session: "Session", entities: list[str] | None = None) -> str:
    targets = (
        set(entities) if entities is not None else {item.id for item in session.document.entities}
    )
    curves = set(entities) if entities is not None else set(session.document.registry.authored)
    output_tasks.schedule(session, curves, explicit=True)
    construction_tasks.evaluate(session, entities)
    captures = {
        item.id
        for item in session.document.entities
        if item.status == "edited" or not item.attachment.binding
    }
    return evaluation.request(session, targets & session.document.index.entities.keys(), captures)
