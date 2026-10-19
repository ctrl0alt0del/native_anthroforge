"""Point coordinate access and retained anatomical frame resolution."""

from dataclasses import replace
from typing import Any

from anthroforge.core.points import Anchor, Point
from anthroforge.native import point_attachments

from . import surface_providers
from .object_frames import Frames


def position(engine: Any, document: Any, item: Point) -> tuple[float, ...]:
    if isinstance(item, Anchor):
        if not item.resolved_position:
            raise ValueError("Anchor has no accepted resolved position.")
        return item.resolved_position
    return tuple(engine.world_point(Frames(engine, document).world(item.id), item.position))


def resolve(engine: Any, document: Any, meshes: Any, item: Anchor, cancel: int) -> Anchor:
    inputs = surface_providers.inputs(engine, document, meshes, (item.binding.reference,))
    if not item.binding.attachment.binding:
        raise ValueError("Anchor has no retained material binding; explicitly rebind it.")
    records = [item.binding.attachment.binding]
    frame = point_attachments.resolve(engine, *inputs, [0], records, cancel)[0]
    return with_frame(item, frame)


def with_frame(item: Anchor, frame: Any) -> Anchor:
    return replace(
        item,
        resolved_position=tuple(frame[[3, 7, 11]].tolist()),
        resolved_frame=tuple(frame.tolist()),
    )
