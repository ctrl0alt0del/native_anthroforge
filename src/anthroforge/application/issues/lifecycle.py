"""Issue setup, invalidation and shutdown shared by all editing contexts."""

from typing import Any

from ..service_lifecycle import Event, Service
from .repairs import register
from .system import IssueSystem


def attach(session: Any) -> Service:
    session.issues = IssueSystem(session)
    register(session)
    return Service(
        "issues",
        (
            (Event.SYNCHRONIZE, session.issues.synchronize),
            (Event.HISTORY_RESTORED, session.issues.reset),
            (Event.CLOSE, session.issues.close),
        ),
    )
