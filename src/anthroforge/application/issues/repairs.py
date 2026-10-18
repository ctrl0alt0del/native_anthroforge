"""Repair adapters use existing explicit operations and coordinator jobs."""

import json
from functools import partial
from typing import TYPE_CHECKING

from anthroforge.core.issues import Issue
from anthroforge.core.reference_images import ReferenceImage

from .resolution import TERMINAL, Repair, Solver

if TYPE_CHECKING:
    from ..session import Session


def editable(session: "Session", issue: Issue) -> bool:
    from ..workspace_policy import included

    if session.waiting_save or session.history.before is not None:
        return False
    return bool(issue.target and included(session.document, session.workspace, issue.target))


def can_evaluate(session: "Session", issue: Issue) -> bool:
    item = session.document.registry.records.get(issue.target)
    return editable(session, issue) and item is not None and not isinstance(item, ReferenceImage)


def can_retry(session: "Session", issue: Issue) -> bool:
    job = session.scheduler.registry.by_id.get(json.loads(issue.evidence).get("job_id", ""))
    return editable(session, issue) and job is not None and job.retryable


def evaluate(session: "Session", issue: Issue) -> tuple[str, ...]:
    from ..control_tasks import request

    previous = set(session.scheduler.registry.by_id)
    if issue.target in session.document.index.controls:
        request(session, issue.target)
    else:
        session.command("evaluate", entities=[issue.target])
    return tuple(session.scheduler.registry.by_id.keys() - previous)


def retry(session: "Session", issue: Issue) -> tuple[str, ...]:
    previous = set(session.scheduler.registry.by_id)
    session.command("job.retry", job_id=json.loads(issue.evidence)["job_id"])
    return tuple(session.scheduler.registry.by_id.keys() - previous)


def register(session: "Session") -> None:
    resolution = session.issues.resolution
    codes = ("EVALUATION_FAILED", "OUTPUT_PENDING", "UPSTREAM_PENDING")
    actions = (
        ("evaluate", "Recalculate target", codes, can_evaluate, evaluate),
        ("retry", "Retry calculation", ("CALCULATION_FAILED",), can_retry, retry),
    )
    for name, label, kinds, applicable, invoke in actions:
        resolution.register(
            Solver(name, label, kinds, partial(applicable, session), partial(invoke, session))
        )


def tick(session: "Session") -> None:
    resolution = session.issues.resolution
    for repair in tuple(resolution.running.values()):
        try:
            advance(session, repair)
        except Exception as error:
            resolution.finish(repair, "FAILED", str(error))


def advance(session: "Session", repair: Repair) -> None:
    resolution = session.issues.resolution
    if repair.state in TERMINAL:
        return
    if repair.state == "VERIFYING":
        resolution.verified(repair)
        return
    jobs = [session.scheduler.registry.by_id[key] for key in repair.jobs]
    if any(job.active for job in jobs) or session.scheduler.blocked:
        return
    failed = next((job for job in jobs if job.state != "succeeded"), None)
    if failed:
        resolution.finish(repair, "FAILED" if failed.error else "CANCELLED", failed.error)
    else:
        resolution.verify(repair)


def cancel(session: "Session", identity: str) -> None:
    resolution = session.issues.resolution
    repair = resolution.running.get(identity)
    if repair is None or repair.state in TERMINAL:
        raise ValueError("No active repair for this issue.")
    for job in repair.jobs:
        session.scheduler.cancel_job(job)
    resolution.finish(repair, "CANCELLED", "Cancellation requested at a safe checkpoint.")
