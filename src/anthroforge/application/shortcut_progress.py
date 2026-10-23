"""Compute readiness from outputs as well as related active jobs."""

from typing import Any

from . import shortcut_effects as effects


def inspect(session: Any, shortcut: str) -> dict[str, Any]:
    value = effects.selected(session, shortcut)
    record = session.shortcut_observation.latest.get(shortcut)
    ports = effects.affected(session, value)
    rows = [effects.row(session, p, set(), set()) for p in ports if meaningful(p.output)]
    jobs = [j.describe() for j in session.scheduler.active_jobs if record and record.id in j.causes]
    state = outcome(session, record, rows, jobs)
    return report(session, shortcut, record, rows, jobs, state)


def report(
    session: Any, shortcut: str, record: Any, rows: Any, jobs: Any, state: str
) -> dict[str, Any]:
    return dict(
        shortcut=shortcut,
        revision=session.document.revision,
        state=state,
        edit=record.id if record else "",
        jobs=jobs,
        blockers=[r for r in rows if incomplete(r)],
        failures=list(record.failures.values()) if record else [],
        updated_outputs=len(record.published) if record else 0,
    )


def meaningful(output: str) -> bool:
    return not output.startswith("property:") and output != "driver"


def incomplete(row: dict[str, Any]) -> bool:
    return bool(row["blocked"] or row["status"] in ("pending", "failed") or row["pending"])


def outcome(session: Any, record: Any, rows: Any, jobs: Any) -> str:
    if record and record.outcome in ("cancelled", "superseded"):
        return str(record.outcome)
    if jobs:
        return "updating"
    if any(r["status"] == "failed" or r["blocked"] for r in rows) or record and record.failures:
        return "failed"
    pending = [r for r in rows if incomplete(r)]
    return waiting(session, pending)


def waiting(session: Any, pending: Any) -> str:
    if any(r["update_mode"] == "MANUAL" or r["pending"] for r in pending):
        return "waiting_manual"
    if (
        pending
        and session.history.before is not None
        and any(r["update_mode"] == "ON_RELEASE" for r in pending)
    ):
        return "waiting_release"
    return "updating" if pending else "complete"
