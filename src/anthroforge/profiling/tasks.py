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
    )


def event(profiler: Any, job: Any, state: str) -> None:
    if profiler is not None and profiler.active:
        metadata = describe(job)
        if job.assessment:
            metadata["workload"] = asdict(job.assessment.workload)
            metadata["delay_ms"] = job.assessment.schedule.delay_ms
        profiler.event("task.lifecycle", state, **metadata)


def call(profiler: Any, job: Any, stage: str, function: Any, *args: Any) -> Any:
    if profiler is None or not profiler.active:
        return function(*args)
    return profiler.call("task", stage, function, *args, _metadata=describe(job))
