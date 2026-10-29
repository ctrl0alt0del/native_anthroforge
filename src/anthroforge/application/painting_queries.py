"""Read-only, bounded projections of current stroke candidates."""

from dataclasses import asdict
from typing import Any

from .painting_consumers import consumer
from .painting_state import Stroke, current


def state(session: Any, value: Stroke) -> str:
    if value.state in ("cancelled", "failed", "committed", "obsolete"):
        return value.state
    return value.state if current(session, value) else "stale"


def describe_stroke(session: Any, value: Stroke) -> dict[str, Any]:
    return dict(
        token=value.token,
        state=state(session, value),
        job=value.job,
        target=value.target,
        consumer=value.consumer,
        error=value.error,
        candidate=value.candidate,
        sequence=value.sequence,
        pending=value.finishing,
        provenance=asdict(value.provenance),
        report=value.asset.get("report", {}) if value.asset else {},
    )


def result(session: Any, value: Stroke, offset: int, limit: int, expected: str) -> dict[str, Any]:
    if not value.asset or state(session, value) in ("stale", "cancelled", "failed", "obsolete"):
        raise ValueError("Painting has no current ready candidate.")
    if expected and expected != value.candidate:
        raise ValueError("Painting candidate changed; restart paging.")
    if type(offset) is not int or type(limit) is not int or offset < 0 or not 1 <= limit <= 16384:
        raise ValueError("Painting pages require a nonnegative offset and limit 1–16384.")
    count, values = consumer(value.consumer).read(value.asset, offset, limit)
    return dict(
        token=value.token, revision=value.candidate, total=count, offset=offset, values=values
    )
