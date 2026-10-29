"""Legacy paint inspection/commit commands delegate to application-owned strokes."""

from typing import Any

from . import painting
from .painting_consumers import name
from .painting_state import get


def preview(session: Any, kind: str, target: str, options: Any) -> dict[str, Any]:
    painting.preview(session, name(kind), target, **options)
    return status(session, kind)


def status(session: Any, kind: str) -> dict[str, Any]:
    value = session.painting.values.get(name(kind))
    if value is None or value.state == "cancelled":
        return dict(state="idle")
    result = painting.status(session, value.token)
    return {key: result[key] for key in ("state", "job", "target", "error", "report")}


def cancel(session: Any, kind: str) -> None:
    if not kind:
        painting.cancel(session)
    elif (value := session.painting.values.get(name(kind))) is not None:
        painting.cancel(session, value.token)


def commit(session: Any, kind: str, job: str) -> None:
    value = session.painting.values.get(name(kind))
    if value is None or value.job != job:
        raise ValueError("The stroke is incomplete or its inputs changed. Paint again.")
    painting.apply(session, value.token)


def current(session: Any, asset: Any) -> bool:
    from .painting_state import current as is_current

    try:
        value = get(session, asset["painting_token"])
        return value.asset is asset and is_current(session, value)
    except (KeyError, ValueError):
        return False
