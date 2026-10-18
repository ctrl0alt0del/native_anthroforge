"""Cancellable background image decoding with atomic authored-step publication."""

from dataclasses import replace
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any

from anthroforge.core.document import Document
from anthroforge.core.jobs import Job
from anthroforge.core.reference_images import ReferenceImage
from anthroforge.core.results import EvaluationResult, Port
from anthroforge.native.mesh import NativeCancellation

from . import authored_jobs, image_assets, object_revisions
from .task_workloads import source_file

if TYPE_CHECKING:
    from .session import Session


def enqueue(
    session: "Session", path: Path, item: ReferenceImage, replacing: bool, origin: int
) -> str:
    current = session.document.registry.construction.get(item.id)
    if current and (not replacing or current.result.revision != item.result.revision):
        return ""
    job = create_job(session, path, item, replacing, origin)
    job.cancel = NativeCancellation(session.engine)
    job.retry = partial(enqueue, session, path, item, replacing, origin)
    job.workload = partial(source_file, path)
    job.provides = frozenset((Port(item.id, "image_resource"),))
    return session.scheduler.submit(job)


def create_job(
    session: "Session", path: Path, item: ReferenceImage, replacing: bool, origin: int
) -> Job:
    job = Job(
        "Load image " + path.name,
        frozenset((item.id,)),
        lambda document: document,
        partial(decode, session, path),
        partial(publish, session, item, replacing, origin),
        kind="image_decode",
        key="image:" + item.id,
    )
    return job


def decode(session: "Session", path: Path, document: Document, cancel: Any) -> Any:
    encoded = path.read_bytes()
    if cancel.is_set():
        raise ValueError("Image import cancelled.")
    asset = image_assets.decode(encoded, session.engine, cancel.handle)
    if cancel.is_set():
        raise ValueError("Image import cancelled.")
    return document, asset


def publish(
    session: "Session", item: ReferenceImage, replacing: bool, origin: int, payload: Any
) -> None:
    document, asset = payload
    if replacing:
        validate_replacement(session, document, item.id)
    else:
        from .image_operations import validate_parent

        validate_parent(session, item)
    merge = partial(replace_assignment if replacing else append_image, item, asset)
    authored_jobs.publish(session, origin, merge)
    session.resources.images.setdefault(asset.digest, asset)


def validate_replacement(session: "Session", document: Document, target: str) -> None:
    from .image_operations import validate_parent

    before, current = document.object(target), session.document.object(target)
    if not isinstance(before, ReferenceImage) or not isinstance(current, ReferenceImage):
        raise ValueError("The image assignment no longer exists.")
    if before.construction_revision != current.construction_revision:
        raise ValueError("Image assignment changed before replacement publication.")
    validate_parent(session, current)


def assigned(item: ReferenceImage, asset: image_assets.ImageAsset) -> ReferenceImage:
    changed = replace(
        item, source=asset.digest, height=item.width * asset.height / asset.width, calibration=None
    )
    revision = item.result.revision + 1
    return replace(changed, result=EvaluationResult(revision=revision))


def append_image(
    item: ReferenceImage, asset: image_assets.ImageAsset, document: Document
) -> Document:
    return authored_jobs.append_object(document, assigned(item, asset))


def replace_assignment(
    item: ReferenceImage, asset: image_assets.ImageAsset, document: Document
) -> Document:
    current = document.registry.construction.get(item.id)
    if not isinstance(current, ReferenceImage):
        return document
    changed = object_revisions.authored(current, assigned(current, asset))
    return replace(
        document, objects=tuple(changed if o.id == item.id else o for o in document.objects)
    )
