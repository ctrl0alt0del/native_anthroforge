"""Issue operations keep discovery and pruning in the issue owner."""

from dataclasses import asdict
from typing import Any

from ..command_contracts import Handler, direct, method, query
from ..issues import commands, repairs


def refreshed(handler: Handler) -> Handler:
    def invoke(session: Any, **arguments: Any) -> Any:
        session.issues.listening.discover_changes()
        session.issues.tasks.prune()
        return handler(session, **arguments)

    return invoke


COMMANDS = (
    query("issues.list", refreshed(method("issues.presentation.query"))),
    query("issues.status", refreshed(method("issues.presentation.status"))),
    query("issues.get", refreshed(method("issues.presentation.get"))),
    direct("issues.recheck", refreshed(method("issues.recheck")), journal=False),
    direct("issues.cancel", refreshed(method("issues.listening.cancel")), journal=False),
    direct("issues.dismiss", refreshed(method("issues.repository.dismiss")), journal=False),
    direct(
        "issues.fix",
        refreshed(lambda session, **a: asdict(session.issues.resolution.invoke(**a))),
        journal=False,
    ),
    query("issues.fixes", refreshed(commands.available)),
    query(
        "issues.repairs",
        refreshed(lambda session: [asdict(r) for r in session.issues.resolution.running.values()]),
    ),
    direct("issues.cancel_fix", refreshed(repairs.cancel), journal=False),
)
