"""Shared headless and desktop issue operations; no implicit repair on inspection."""

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from . import repairs

if TYPE_CHECKING:
    from ..session import Session


def execute(session: "Session", operation: str, arguments: dict[str, Any]) -> Any:
    commands = catalogue(session)
    if operation not in commands:
        raise ValueError("Unknown issue operation: " + operation)
    return commands[operation](**arguments)


def catalogue(session: "Session") -> dict[str, Any]:
    system = session.issues
    return {
        "issues.list": system.presentation.query,
        "issues.status": system.presentation.status,
        "issues.get": system.presentation.get,
        "issues.recheck": system.recheck,
        "issues.cancel": system.listening.cancel,
        "issues.dismiss": system.repository.dismiss,
        "issues.fix": lambda **a: asdict(system.resolution.invoke(**a)),
        "issues.fixes": lambda **a: available(session, **a),
        "issues.repairs": lambda: [asdict(value) for value in system.resolution.running.values()],
        "issues.cancel_fix": lambda **a: repairs.cancel(session, **a),
    }


def available(session: "Session", identity: str) -> list[dict[str, str]]:
    system = session.issues
    issue = system.repository.records.get(identity)
    if issue is None:
        return []
    return [
        dict(name=solver.name, label=solver.label) for solver in system.resolution.available(issue)
    ]
