"""Stroke creation owns an authored transaction while fitting runs in the coordinator."""

from functools import partial
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from anthroforge.core.drawing import FitSettings

from . import authored_jobs, drawing_tasks, placement_inputs
from .object_creation import placement
from .operations import require_name

if TYPE_CHECKING:
    from .session import Session


def draw(
    session: "Session",
    points: list[list[float]],
    settings: dict[str, Any] | None = None,
    name: str = "Drawn curve",
    parent: str = "",
    owner: str = "",
    values: list[float] | None = None,
    projection: Any = None,
) -> dict[str, str]:
    location = placement(session, parent, owner, values)
    metadata = dict(id=str(uuid4()), name=require_name(name), **location)
    return submit(session, metadata, points, settings, projection)


def submit(
    session: "Session", metadata: Any, points: Any, settings: Any, projection: Any
) -> dict[str, str]:
    options = FitSettings(**(settings or {}))
    samples = drawing_tasks.stroke_samples(points)
    request = drawing_tasks.Request(
        metadata, samples, options, placement_inputs.validated(projection, len(samples))
    )
    enqueue = partial(drawing_tasks.enqueue, session, request)
    return dict(object_id=metadata["id"], job_id=authored_jobs.begin(session, enqueue))
