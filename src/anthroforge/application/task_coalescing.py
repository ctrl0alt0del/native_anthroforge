"""Reuse uncaptured requests; running work retains normal cancellation and read checks."""

from typing import Any

from anthroforge.core.jobs import Job
from anthroforge.profiling import tasks as trace


def renewable(job: Job) -> bool:
    return (
        job.state == "queued"
        and not job.obsolete
        and job.renew_inputs is not None
        and job.inputs_key is not None
    )


def compatible(before: Job, after: Job) -> bool:
    fields = (
        "kind",
        "outputs",
        "provides",
        "writes",
        "publish_during_edit",
        "restart_on_redo",
        "edit_contexts",
    )
    return (
        renewable(before)
        and renewable(after)
        and all(getattr(before, field) == getattr(after, field) for field in fields)
    )


def reuse(coordinator: Any, request: Job) -> str:
    if not request.key or not renewable(request):
        return ""
    for pending in coordinator.registry.matching("key", (request.key,)):
        if compatible(pending, request):
            pending.priority = request.priority
            pending.interactive |= request.interactive
            pending.label = request.label
            trace.event(coordinator.profiler, pending, "coalesced")
            request.retire()
            return str(pending.id)
    return ""
