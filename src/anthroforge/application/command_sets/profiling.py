"""Profiler controls bypass their own tracing while retaining task-boundary snapshots."""

from anthroforge.profiling.tasks import operation

from ..command_contracts import direct

COMMANDS = (
    direct(
        "profile.start",
        lambda session, **a: operation(session, "profile.start", a),
        journal=False,
        profiled=False,
    ),
    direct(
        "profile.status",
        lambda session, **a: operation(session, "profile.status", a),
        journal=False,
        profiled=False,
    ),
    direct(
        "profile.stop",
        lambda session, **a: operation(session, "profile.stop", a),
        journal=False,
        profiled=False,
    ),
)
