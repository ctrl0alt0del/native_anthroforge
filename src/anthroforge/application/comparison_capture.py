"""Freeze comparison evidence at request time, independently of later baseline replacement."""

import json
from dataclasses import dataclass
from typing import Any, cast

from . import inspection, shortcut_comparison


@dataclass(frozen=True)
class ComparisonCapture:
    baseline: shortcut_comparison.Baseline
    evidence: dict[str, Any]
    issues: dict[str, Any]
    journal: dict[str, Any]
    replay: bool


def capture(session: Any, replay: bool = False) -> ComparisonCapture | None:
    state = session.shortcut_comparison
    if state.baseline is None:
        if replay:
            raise ValueError("Capture a comparison baseline before requesting replay evidence.")
        return None
    journal = journal_snapshot(session)
    try:
        evidence = shortcut_comparison.evidence(session, state.baseline.shortcut)
    except ValueError as error:
        evidence = dict(unavailable=str(error))
    return ComparisonCapture(
        state.baseline, evidence, inspection.issue_records(session), journal, replay
    )


def journal_snapshot(session: Any) -> dict[str, Any]:
    state = session.shortcut_comparison
    if (state.baseline.source.routing_backend != session.preferences.value.routing_backend
            or state.baseline.source.fiber_propagation != session.preferences.value.fiber_propagation):
        state.journal.invalidate("Execution preferences changed after baseline capture.")
    value = dict(state.journal.describe(), operations=state.journal.events)
    if session.history.before is not None:
        value["complete"] = False
        value["reasons"].append("Capture ends inside an unfinished gesture.")
    return cast(dict[str, Any], json.loads(json.dumps(value, allow_nan=False)))
