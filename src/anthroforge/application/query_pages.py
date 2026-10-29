"""Bounded, revision-qualified reads shared by authoring query adapters."""

from typing import Any


def bounds(offset: Any = 0, limit: Any = 4096) -> Any:
    if type(offset) is not int or offset < 0:
        raise ValueError("offset must be a nonnegative integer.")
    if type(limit) is not int or not 1 <= limit <= 16384:
        raise ValueError("limit must be an integer from 1 to 16384.")
    return offset, offset + limit


def require_revision(expected: Any, actual: Any) -> Any:
    if expected is not None and expected != actual:
        raise ValueError("Query inputs changed; restart paging with the current revision.")
