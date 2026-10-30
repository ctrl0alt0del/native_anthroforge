"""Shortcut gesture/observation lifetime belongs to shortcuts, not Session."""

from functools import partial
from typing import Any

from .comparison_journal import record
from .formula_invalidation import FormulaInvalidation
from .service_lifecycle import Event, Service
from .shortcut_comparison import Comparison
from .shortcut_contexts import Contexts
from .shortcut_observation import Observation


def attach(session: Any) -> Service:
    session.shortcut_edits = Contexts(session)
    session.formula_invalidation = FormulaInvalidation()
    session.shortcut_observation = Observation(session)
    session.shortcut_comparison = Comparison(session)
    session.scheduler.observer = session.shortcut_observation.event
    session.scheduler.annotate = session.shortcut_edits.annotate
    session.scheduler.before_dispatch = session.shortcut_edits.require
    return Service("shortcuts", hooks(session))


def hooks(session: Any) -> tuple[Any, ...]:
    return (
        (Event.SYNCHRONIZE, session.shortcut_edits.synchronize),
        (Event.SYNCHRONIZE, session.shortcut_observation.prune),
        (Event.GESTURE_BEGIN, partial(begin, session)),
        (Event.GESTURE_COMMITTED, partial(commit, session)),
        (Event.GESTURE_CANCELING, partial(cancel, session)),
        (Event.HISTORY_BEGIN, partial(navigate, session)),
        (Event.CLOSE, session.shortcut_comparison.clear),
    )


def begin(session: Any) -> None:
    session.shortcut_edits.active = ""
    record(session, "begin")


def commit(session: Any) -> None:
    session.shortcut_edits.active = ""
    session.shortcut_observation.finish_gesture()
    record(session, "commit")


def cancel(session: Any) -> None:
    record(session, "cancel")
    session.shortcut_observation.finish_gesture(cancelled=True)
    session.shortcut_edits.active = ""


def navigate(session: Any, direction: int) -> None:
    record(session, "undo" if direction < 0 else "redo")
    session.shortcut_observation.restore()
