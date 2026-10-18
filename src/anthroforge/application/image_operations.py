"""Reference-image authoring uses ordinary objects, shared history and owned resources."""

from dataclasses import replace
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from anthroforge.core.entities import IDENTITY
from anthroforge.core.reference_images import ImageCalibration, ReferenceImage
from anthroforge.native import images

from . import authored_jobs, curve_sources, image_tasks, object_operations
from .operations import require_name

if TYPE_CHECKING:
    from .session import Session


def selected(session: "Session", target: str) -> ReferenceImage:
    item = object_operations.editable(session, target)
    if not isinstance(item, ReferenceImage):
        raise ValueError("Select a reference image.")
    return item


def import_image(
    session: "Session",
    path: str,
    width: float = 1.0,
    name: str = "",
    parent: str = "",
    owner: str = "",
    values: list[float] | None = None,
) -> dict[str, str]:
    source = Path(path).resolve(strict=True)
    location = placement(session, parent, owner, values)
    item = new_image(session, source, width, name, location)
    request = partial(image_tasks.enqueue, session, source, item, False)
    return dict(object_id=item.id, job_id=authored_jobs.begin(session, request))


def new_image(
    session: "Session", source: Path, width: float, name: str, location: dict[str, Any]
) -> ReferenceImage:
    item = ReferenceImage(
        name=require_name(name or source.stem),
        source="@pending",
        width=width,
        **location,
    )
    validate_parent(session, item)
    return item


def placement(
    session: "Session", parent: str, owner: str, values: list[float] | None
) -> dict[str, Any]:
    if owner:
        session.editable(owner)
    frame = session.engine.transform(values) if values is not None else IDENTITY
    return dict(parent=parent, owners=(owner,) if owner else (), matrix=frame)


def validate_parent(session: "Session", item: ReferenceImage) -> None:
    if item.parent:
        parent = session.document.object(item.parent)
        if isinstance(parent, ReferenceImage):
            raise ValueError("Reference images cannot parent other objects.")


def replace_source(session: "Session", target: str, path: str) -> dict[str, str]:
    item, source = selected(session, target), Path(path).resolve(strict=True)
    request = partial(image_tasks.enqueue, session, source, item, True)
    return dict(object_id=target, job_id=authored_jobs.begin(session, request))


def instance(session: "Session", source: str, name: str = "") -> str:
    original = selected(session, source)
    item = replace(original, id=str(uuid4()), name=require_name(name or original.name + " copy"))
    session.replace_document(objects=(*session.document.objects, item))
    return item.id


def size(session: "Session", target: str, width: float) -> None:
    item = selected(session, target)
    asset = session.resources.images[item.source]
    height = width * asset.height / asset.width
    object_operations.install(session, replace(item, width=width, height=height, calibration=None))


def align(session: "Session", target: str, axis: str) -> None:
    selected(session, target)
    orientations = {"X": (0, 90, 0), "Y": (-90, 0, 0), "Z": (0, 0, 0)}
    if axis not in orientations:
        raise ValueError("Image alignment requires X, Y or Z.")
    frame = curve_sources.world(session.engine, session.document, target)
    values = list(session.engine.decompose(frame))
    values[3:6] = orientations[axis]
    object_operations.transform(session, target, values, world=True)


def calibrate(
    session: "Session", target: str, first: list[float], second: list[float], distance: float
) -> None:
    item = selected(session, target)
    calibration = ImageCalibration(landmark(first), landmark(second), distance)
    frame = curve_sources.world(session.engine, session.document, target)
    width, height = images.calibrate(
        session.engine, frame, [item.width, item.height], [*first, *second], distance
    )
    object_operations.install(
        session, replace(item, width=width, height=height, calibration=calibration)
    )


def landmark(values: list[float]) -> tuple[float, float]:
    if len(values) != 2:
        raise ValueError("Image landmarks use normalized 2D image coordinates.")
    return values[0], values[1]


def inspect(session: "Session", target: str) -> dict[str, Any]:
    item = session.document.object(target)
    if not isinstance(item, ReferenceImage):
        raise ValueError("Select a reference image.")
    asset = session.resources.images[item.source]
    return dict(
        source=item.source,
        pixels=[asset.width, asset.height],
        format=asset.format,
        dimensions=[item.width, item.height],
        calibrated=item.calibration is not None,
    )
