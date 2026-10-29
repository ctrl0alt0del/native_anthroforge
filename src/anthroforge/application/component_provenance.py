"""Accepted editing provenance, including parent changes awaiting Manual evaluation."""

from typing import Any

from anthroforge.core.results import Port

from .construction_policy import revision


def pending(document: Any, item: Any) -> tuple[str, ...]:
    result = getattr(item, "result", None)
    changed = {
        read.owner
        for read in getattr(result, "inputs", ())
        if read.owner != item.id and differs(document, read)
    }
    return tuple(sorted(changed | set(getattr(result, "pending", ()))))


def differs(document: Any, read: Any) -> bool:
    try:
        return bool(read != revision(document, Port(read.owner, read.output)))
    except (KeyError, ValueError):
        return True
