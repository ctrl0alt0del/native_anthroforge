"""Coordinator jobs own stroke computation and finalization; no UI callbacks."""

from functools import partial
from typing import Any

from anthroforge.core.jobs import Job
from anthroforge.native.mesh import NativeCancellation

from .inspection_context import freeze
from .painting_consumers import consumer
from .painting_state import require_current


def request(session: Any, value: Any) -> None:
    definition = consumer(value.consumer)
    options = dict(value.options, samples=value.inputs.samples, brush=value.inputs.brush.native())
    cached = value.asset if value.finishing and value.candidate_sequence == value.sequence else None
    job = create_job(session, value, options, cached)
    job.cancel = NativeCancellation(session.engine)
    job.workload = lambda _: definition.workload(session, value.target, options)
    job.cleanup = partial(completed, session, value, job)
    value.job, value.state, value.error = job.id, "queued", ""
    session.scheduler.submit(job)


def create_job(session: Any, value: Any, options: Any, cached: Any) -> Job:
    return Job(
        "Paint " + value.consumer,
        frozenset((value.target,)) if value.finishing else frozenset(),
        partial(capture, session, value, options, cached),
        partial(compute, value.consumer, value.target, options),
        partial(publish, session, value, value.sequence, options),
        key="painting:" + value.consumer,
        kind="painting",
        writes=value.finishing,
        priority=-5,
        interactive=value.interactive and not value.finishing,
        publish_during_edit=not value.finishing,
    )


def capture(session: Any, value: Any, options: Any, cached: Any, document: Any) -> Any:
    require_current(session, value)
    value.state = "running"
    return (None if cached else freeze(session)), cached


def compute(kind: str, target: str, options: Any, captured: Any, cancel: Any) -> Any:
    context, cached = captured
    return (
        cached
        if cached is not None
        else consumer(kind).compute(context, target, options, cancel.handle)
    )


def publish(session: Any, value: Any, sequence: int, options: Any, output: Any) -> None:
    if session.painting.values.get(value.consumer) is not value or value.sequence != sequence:
        raise ValueError("Painting candidate was superseded.")
    require_current(session, value)
    value.asset = candidate(value, options, output)
    value.state, value.candidate_sequence = "ready", sequence
    value.candidate = value.token + ":" + str(sequence)
    if value.finishing:
        session.command("painting.commit", token=value.token)


def candidate(value: Any, options: Any, output: Any) -> dict[str, Any]:
    return dict(
        output,
        stamp=value.stamp,
        options=options,
        target=value.target,
        kind=consumer(value.consumer).kind,
        painting_token=value.token,
    )


def completed(session: Any, value: Any, job: Job, state: str) -> None:
    if value.job != job.id or state == "succeeded":
        return
    value.state, value.error, value.finishing = state, job.error, False
    value.asset = None
    if session.painting.active == value.token:
        session.painting.active = ""
