"""Cancellable embedded reference/evidence imports own inputs and one authored undo step."""

from dataclasses import replace
from functools import partial
from pathlib import Path
from typing import Any

from anthroforge.core.jobs import Job
from anthroforge.native.mesh import NativeCancellation

from . import authored_jobs, reconstruction_state, task_workloads


def start(session: Any, path: str, group: str, row: Any, worker: Any) -> dict[str, str]:
    reconstruction_state.variant_operations.require_idle(session)
    source = Path(path).resolve(strict=True)
    with session.contexts.use(""):
        session.begin()
        try:
            job = authored_jobs.begin(
                session, partial(enqueue, session, source, group, row, worker)
            )
            session.commit()
        except Exception:
            session.cancel()
            raise
    return dict(id=row.id, job_id=job)


def enqueue(session: Any, path: Path, group: str, row: Any, worker: Any, origin: int) -> str:
    job = Job(
        "Import reconstruction " + path.name,
        frozenset((row.id,)),
        lambda _: None,
        lambda _, cancel: worker(path, row, cancel),
        partial(publish, session, group, origin),
        kind="mesh_import",
        cancel=NativeCancellation(session.engine),
        workload=partial(task_workloads.source_file, path),
    )
    job.retry = partial(enqueue, session, path, group, row, worker, origin)
    return session.scheduler.submit(job)


def publish(session: Any, group: str, origin: int, result: Any) -> None:
    row, resource, payload = result
    resource_group = "evidence" if group == "evidence" else "meshes"
    getattr(session.resources, resource_group)[resource] = payload
    authored_jobs.publish(session, origin, partial(merge, group, row))


def merge(group: str, row: Any, document: Any) -> Any:
    value = document.reconstruction
    if any(existing.id == row.id for existing in getattr(value, group)):
        return document
    if group == "stages":
        scene = value.snapshot(value.variant(row.variant).current) if row.variant else document
        if row.subject not in scene.registry.anatomy:
            return document
    value = replace(value, **{group: (*getattr(value, group), row)})
    return replace(document, reconstruction=value)
