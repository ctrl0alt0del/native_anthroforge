"""Origin relocation preserves ordinary children and consumer placement atomically."""

from dataclasses import replace
from typing import Any

from anthroforge.native.construction import matrix

from . import consumer_parenting, object_revisions


def relocate(session: Any, before: Any, after: Any) -> None:
    entities = tuple(after if e.id == after.id else e for e in session.document.entities)
    objects = tuple(rebase_object(session, o, before, after) for o in session.document.objects)
    controls = tuple(rebase_control(session, c, before, after) for c in session.document.controls)
    document = replace(session.document, entities=entities, objects=objects, controls=controls)
    document = consumer_parenting.rebind(session, document, before.id)
    session.scheduler.invalidate({before.id, *(c.id for c in controls if c.follow == before.id)})
    session.replace_document(
        entities=document.entities, objects=document.objects, controls=controls
    )


def local(session: Any, item: Any, before: Any, after: Any) -> tuple[float, ...]:
    world = matrix(session.engine, before.matrix, item.matrix)
    return matrix(session.engine, after.matrix, world, relative=True)


def rebase_object(session: Any, item: Any, before: Any, after: Any) -> Any:
    if item.parent != before.id:
        return item
    return object_revisions.authored(
        item, replace(item, matrix=local(session, item, before, after))
    )


def rebase_control(session: Any, item: Any, before: Any, after: Any) -> Any:
    if item.follow != before.id:
        return item
    return replace(item, matrix=local(session, item, before, after), generation=item.generation + 1)
