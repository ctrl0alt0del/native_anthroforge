"""One lifecycle for command guards, implicit transactions and comparison recording."""

from typing import Any

from . import comparison_journal, mirror_policy, variant_policy
from .command_contracts import Command


def execute(session: Any, command: Command, arguments: dict[str, Any]) -> Any:
    require(session, command, arguments)
    if command.policy.transaction:
        return transaction(session, command, arguments)
    return invoke(session, command, arguments)


def require(session: Any, command: Command, arguments: dict[str, Any]) -> None:
    policy = command.policy
    if policy.mirror_guard:
        mirror_policy.require_edit(arguments)
    if policy.variant_guard:
        variant_policy.command(session, arguments, project_scope=policy.project_scope)
    if policy.isolated and session.history.before is not None:
        raise ValueError("Finish the current gesture before committing this operation.")


def transaction(session: Any, command: Command, arguments: dict[str, Any]) -> Any:
    implicit = session.history.before is None
    if implicit:
        session.begin()
    try:
        result = invoke(session, command, arguments)
        if implicit:
            session.commit()
        return result
    except Exception:
        if implicit and session.history.before is not None:
            session.cancel()
        raise


def invoke(session: Any, command: Command, arguments: dict[str, Any]) -> Any:
    result = command.handler(session, **arguments)
    policy = command.policy
    if policy.journal == "edit":
        comparison_journal.record(session, command.name, arguments, authored=True)
    elif policy.journal == "direct" and command.name not in comparison_journal.BOUNDARIES:
        comparison_journal.record(session, command.name, arguments)
    return result
