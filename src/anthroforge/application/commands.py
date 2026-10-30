"""Immutable feature catalogue and the shared application command entry point."""

from collections.abc import Mapping
from functools import cache
from typing import Any

from anthroforge.profiling.tasks import command_metadata

from .command_contracts import Command, catalogue
from .command_execution import execute as run


@cache
def registered() -> Mapping[str, Command]:
    from .command_sets import GROUPS

    return catalogue(GROUPS)


def execute(session: Any, operation: str, arguments: dict[str, Any]) -> Any:
    command = registered().get(operation)
    if command is None:
        raise ValueError(f"Unknown operation: {operation}")
    if not command.profiled:
        return run(session, command, arguments)
    return session.profiler.call(
        "command",
        operation,
        run,
        session,
        command,
        arguments,
        _metadata=command_metadata(session, arguments),
    )
