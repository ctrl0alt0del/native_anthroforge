"""Capture lifecycle identity at the coordinator boundary without changing scheduling."""

from dataclasses import asdict
from typing import Any


def describe(job):
    return dict(
        job=job.id,
        kind=job.kind,
        origin=job.origin,
        epoch=job.epoch,
        revision=job.snapshot.revision if job.snapshot else None,
        outputs=sorted(job.outputs)[:128],
        reads=sorted(job.reads)[:128],
        output_count=len(job.outputs),
        execution=job.execution,
        obsolete=job.obsolete,
        timing=timing(job),
    )


def event(profiler: Any, job: Any, state: str) -> None:
    if profiler is not None and profiler.active:
        metadata = describe(job)
        if job.assessment:
            metadata["workload"] = asdict(job.assessment.workload)
            metadata["delay_ms"] = job.assessment.schedule.delay_ms
        profiler.event("task.lifecycle", state, **metadata)


def timing(job):
    return dict(
        queued_us=(job.queued_since or job.created) * 1_000_000,
        ready_us=job.ready_at * 1_000_000,
        started_us=job.started * 1_000_000,
        cancel_requested_us=job.cancel_requested * 1_000_000,
    )


def operation(session: Any, name: str, arguments: dict[str, Any]) -> Any:
    if name == "profile.stop":
        snapshot(session, "active_at_stop")
    result = session.profiler.operation(name, arguments)
    if name == "profile.start":
        snapshot(session, "active_at_start")
    return result


def snapshot(session, state):
    if not session.profiler.active:
        return
    document_snapshot(session, state)
    active = (job for job in session.scheduler.jobs if job.active)
    for index, job in enumerate(active):
        if index >= 4096:
            session.profiler.losses["job_snapshot_limit"] += 1
            break
        event(session.profiler, job, state)


def document_snapshot(session, state):
    session.profiler.event(
        "document",
        state,
        document=str(session.document.id),
        revision=session.document.revision,
        entities=len(session.document.entities),
        controls=len(session.document.controls),
    )


def call(profiler: Any, job: Any, stage: str, function: Any, *args: Any) -> Any:
    if profiler is None or not profiler.active:
        return function(*args)
    return profiler.call("task", stage, function, *args, _metadata=describe(job))


def command_metadata(session: Any, arguments: dict[str, Any]) -> dict[str, Any] | None:
    if not session.profiler.active:
        return None
    metadata: dict[str, Any] = {
        "document": str(session.document.id),
        "revision": session.document.revision,
    }
    for key in ("entity", "curve", "point", "control", "binding", "job_id"):
        value = arguments.get(key)
        if isinstance(value, str):
            metadata[key] = value[:128]
    return metadata
