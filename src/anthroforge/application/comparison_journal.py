"""Bounded semantic replay evidence; observing edits never changes their execution."""

import json
from time import monotonic
from typing import Any

SUPPORTED = frozenset(("shortcut.set", "driver.value", "evaluate", "curve.evaluate"))
BOUNDARIES = frozenset(("begin", "commit", "cancel", "wait"))


class Journal:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.reasons: list[str] = []
        self.started, self.bytes, self.stopped = monotonic(), 0, False

    def invalidate(self, reason: str) -> None:
        if reason not in self.reasons and len(self.reasons) < 128:
            self.reasons.append(reason[:2000])

    def append(self, operation: str, arguments: Any = None) -> None:
        if self.stopped:
            return
        event = dict(
            operation=operation, arguments=arguments or {}, seconds=monotonic() - self.started
        )
        encoded = encode(self, event)
        if encoded is not None:
            self.store(encoded)

    def store(self, encoded: str) -> None:
        if len(self.events) >= 10000 or self.bytes + len(encoded.encode()) > 16 * 1024 * 1024:
            self.invalidate("Replay journal limit reached; later edits were not recorded.")
            self.stopped = True
            return
        self.events.append(json.loads(encoded))
        self.bytes += len(encoded.encode())

    def describe(self) -> dict[str, Any]:
        return dict(
            complete=not self.reasons,
            reasons=list(self.reasons),
            events=len(self.events),
            bytes=self.bytes,
            stopped=self.stopped,
        )


def encode(journal: Journal, event: Any) -> str | None:
    try:
        return json.dumps(event, allow_nan=False)
    except (TypeError, ValueError):
        journal.invalidate("An operation contained non-serializable arguments.")
        journal.stopped = True
        return None


def record(session: Any, operation: str, arguments: Any = None, authored: bool = False) -> None:
    state = session.shortcut_comparison
    if state.baseline is None:
        return
    if operation in SUPPORTED | BOUNDARIES:
        state.journal.append(operation, arguments)
    elif authored or operation in ("undo", "redo", "preferences.set", "job.cancel", "job.retry"):
        state.journal.invalidate("Unrecorded state change: " + operation)


def edit(session: Any, operation: str, arguments: Any, function: Any) -> Any:
    result = function(session, **arguments)
    record(session, operation, arguments, authored=True)
    return result


def direct(session: Any, operation: str, arguments: Any, function: Any) -> Any:
    result = function(**arguments)
    if operation not in BOUNDARIES:
        record(session, operation, arguments)
    return result
