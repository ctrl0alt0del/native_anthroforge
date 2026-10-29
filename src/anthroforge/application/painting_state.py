"""Context-local bounded stroke ownership, separate from document and inspection."""

from dataclasses import dataclass, field
from typing import Any, cast
from uuid import uuid4

from anthroforge.core.painting import Provenance, StrokeInput


@dataclass
class Stroke:
    consumer: str
    target: str
    inputs: StrokeInput
    options: dict[str, Any]
    stamp: Any
    provenance: Provenance
    token: str = field(default_factory=lambda: str(uuid4()))
    state: str = "drawing"
    job: str = ""
    asset: dict[str, Any] | None = None
    error: str = ""
    sequence: int = 0
    candidate: str = ""
    candidate_sequence: int = -1
    finishing: bool = False
    interactive: bool = False
    deadline: float | None = None


@dataclass
class Painting:
    values: dict[str, Stroke] = field(default_factory=dict)
    active: str = ""


def get(session: Any, token: str) -> Stroke:
    found = next((row for row in session.painting.values.values() if row.token == token), None)
    if found is None:
        raise ValueError("Unknown or replaced painting token.")
    return cast(Stroke, found)


def current(session: Any, value: Stroke) -> bool:
    from .painting_consumers import consumer

    try:
        return bool(
            consumer(value.consumer).signature(session, value.target, value.options) == value.stamp
        )
    except (ValueError, KeyError):
        return False


def require_current(session: Any, value: Stroke) -> None:
    if not current(session, value):
        raise ValueError("Painting inputs changed; paint the current surface again.")


def presented(session: Any, kind: str) -> Any:
    from .painting_consumers import name

    value = session.painting.values.get(name(kind))
    if value and value.asset and value.state != "committed" and current(session, value):
        return value.asset
    return None
