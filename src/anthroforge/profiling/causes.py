"""Bounded causal evidence at shared mutation and scheduling boundaries."""

from itertools import islice
from typing import Any


def document(session: Any, before: Any, after: Any) -> None:
    profiler = session.profiler
    if not profiler.active or before is after:
        return
    delta = session.changes.records[-1][1]
    profiler.event(
        "revision",
        "changed",
        document=str(after.id),
        before=before.revision,
        after=after.revision,
        producer_job=getattr(profiler.resources.local, "job", ""),
        **mutation_fields(delta),
    )


def mutation_fields(delta):
    count = len(delta.entities) + len(delta.controls) + len(delta.objects)
    changes = (
        dict(kind=kind, entity=key, fields=sorted(fields))
        for kind in ("entities", "controls", "objects")
        for key, fields in getattr(delta, kind).items()
    )
    return dict(
        fields=sorted(delta.document),
        reset=delta.reset,
        changes=list(islice(changes, 16)),
        changed_count=count,
        details_truncated=count > 16,
    )


def invalidated(coordinator: Any, affected: Any, reason: str, ports: bool = False) -> None:
    profiler = coordinator.profiler
    if profiler is None or not profiler.active or not affected:
        return
    profiler.event(
        "invalidation",
        reason,
        revision=coordinator.current().revision,
        targets=target_records(affected, ports),
        target_count=len(affected),
        details_truncated=len(affected) > 64,
    )


def target_records(affected, ports):
    if not ports:
        return sorted(affected)[:64]
    return [
        dict(owner=p.owner, output=p.output)
        for p in sorted(affected, key=lambda p: (p.owner, p.output))[:64]
    ]


def cancellation(coordinator: Any, job: Any, reason: str, replacement: str) -> None:
    profiler = coordinator.profiler
    if profiler is not None and profiler.active:
        profiler.event(
            "invalidation",
            "cancel_job",
            job=job.id,
            reason=reason,
            replacement_job=replacement,
            revision=coordinator.current().revision,
        )
