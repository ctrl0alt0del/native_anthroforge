"""Stable bounded projections of existing domain choice policies."""

from hashlib import sha256
from typing import Any
from uuid import uuid4

from . import query_pages


def revision(session: Any, key: Any) -> str:
    previous = session._editing.values.get("query_revision")
    if previous is None or previous[0] is not session.document:
        previous = session.document, str(uuid4())
        session._editing.values["query_revision"] = previous
    return sha256(repr((previous[1], key)).encode()).hexdigest()


def project(
    session: Any,
    rows: Any,
    key: Any,
    search: str = "",
    offset: int = 0,
    limit: int = 4096,
    expected_revision: str | None = None,
) -> dict[str, Any]:
    start, end = query_pages.bounds(offset, limit)
    signature = revision(session, (key, search))
    query_pages.require_revision(expected_revision, signature)
    return page(ordered(rows, search), start, end, signature)


def ordered(rows: Any, search: str) -> Any:
    return sorted(
        (r for r in rows if search.casefold() in str(r.get("name", "")).casefold()),
        key=lambda r: (
            str(r.get("name", "")).casefold(),
            str(r.get("key", r.get("property", r.get("id", "")))),
        ),
    )


def page(selected: Any, start: int, end: int, signature: str) -> dict[str, Any]:
    return dict(
        items=selected[start:end],
        total=len(selected),
        offset=start,
        next_offset=end if end < len(selected) else None,
        revision=signature,
    )
