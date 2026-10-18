"""Explicit presentation operations shared by desktop and headless inspection."""

from typing import Any

from . import bookmarks, measurements
from .session import Session

OPERATIONS = {
    "measurement.point": measurements.point,
    "measurement.add": measurements.add,
    "measurement.remove": measurements.remove,
    "measurement.list": measurements.inspect,
    "bookmark.add": bookmarks.add,
    "bookmark.restore": bookmarks.restore,
    "bookmark.rename": bookmarks.rename,
    "bookmark.remove": bookmarks.remove,
    "bookmark.list": bookmarks.inspect,
}


def execute(session: Session, operation: str, arguments: dict[str, Any]) -> Any:
    if operation not in OPERATIONS:
        raise ValueError("Unknown inspection operation: " + operation)
    return OPERATIONS[operation](session, **arguments)  # type: ignore[operator]
