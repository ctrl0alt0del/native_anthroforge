"""Shared headless and desktop issue operations; no implicit repair on inspection."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..session import Session


def available(session: "Session", identity: str) -> list[dict[str, str]]:
    system = session.issues
    issue = system.repository.records.get(identity)
    if issue is None:
        return []
    return [
        dict(name=solver.name, label=solver.label) for solver in system.resolution.available(issue)
    ]
