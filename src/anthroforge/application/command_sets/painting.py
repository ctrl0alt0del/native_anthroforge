"""Painting operation declarations; common execution lives in command_execution."""

from .. import painting, painting_commands
from ..command_contracts import direct, edit, query

COMMANDS = (
    edit("painting.commit", painting.apply, isolated=True),
    query("painting.describe", painting_commands.describe),
    direct("painting.begin", painting.begin, journal=False),
    direct("painting.append", painting.append, journal=False),
    direct("painting.finish", painting.finish, journal=False),
    direct("painting.preview", painting.preview, journal=False),
    query("painting.status", painting.status),
    query("painting.result", painting.result),
    direct("painting.cancel", painting.cancel, journal=False),
)
