"""Inspection operation declarations; common execution lives in command_execution."""

from .. import (
    comparison_replay,
    editing_queries,
    inspection,
    inspection_report,
    inspection_snapshots,
)
from ..command_contracts import direct, query
from ..inspection_commands import OPERATIONS

COMMANDS = (
    direct("inspect.target", lambda session, **a: inspection.target(session, **a)),
    direct("inspect.snapshot", lambda session, **a: inspection.snapshot(session, **a)),
    direct("editing.inspect", lambda session, **a: editing_queries.inspect(session, **a)),
    direct("inspection.export", lambda session, **a: inspection_report.export(session, **a)),
    direct("inspection.capture", lambda session, **a: inspection_snapshots.capture(session, **a)),
    direct(
        "inspection.capture.status", lambda session, **a: inspection_snapshots.status(session, **a)
    ),
    direct("inspection.geometry", lambda session, **a: inspection_snapshots.geometry(session, **a)),
    direct("inspection.release", lambda session, **a: inspection_snapshots.release(session, **a)),
    direct("inspection.replay", lambda session, **a: comparison_replay.replay(**a)),
    *(query(name, handler) for name, handler in OPERATIONS.items()),
)
