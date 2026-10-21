"""Parameter edits use the common primitive validation, scheduling and undo boundary."""

from dataclasses import replace
from typing import Any

from anthroforge.core.segment_chain import Segment

from . import primitive_operations as primitives
from .construction_codec import tuples


def configure(session: Any, entity: str, **options: Any) -> None:
    definition = primitives.definition(session, entity)
    if definition.chain is None or set(options) - {"spread", "bend_mode", "profile", "unite"}:
        raise ValueError("Choose a Segment Chain and valid chain parameters.")
    chain = replace(definition.chain, **tuples(options))
    primitives.install(session, entity, replace(definition, chain=chain))


def segment(session: Any, entity: str, index: int, **options: Any) -> None:
    definition = primitives.definition(session, entity)
    if definition.chain is None or not 0 <= index < len(definition.chain.segments):
        raise ValueError("Choose an existing segment.")
    values = list(definition.chain.segments)
    values[index] = replace(values[index], **options)
    primitives.install(
        session,
        entity,
        replace(definition, chain=replace(definition.chain, segments=tuple(values))),
    )


def resize(session: Any, entity: str, count: int) -> None:
    definition = primitives.definition(session, entity)
    if definition.chain is None or type(count) is not int or not 1 <= count <= 32:
        raise ValueError("A Segment Chain supports 1–32 segments.")
    values = definition.chain.segments[:count]
    values += (Segment(),) * (count - len(values))
    chain = replace(definition.chain, segments=values)
    primitives.install(session, entity, replace(definition, chain=chain))
