"""Direct lifecycle reports; Activity history is not a diagnostic repository."""

from typing import TYPE_CHECKING, Any

from anthroforge.core.issues import Issue, evidence, fingerprint
from anthroforge.core.jobs import Job

from .reporting import Reporting

if TYPE_CHECKING:
    from ..session import Session


class TaskReports:
    name = "tasks.v1"

    def __init__(self, session: "Session", reporting: Reporting) -> None:
        self.session, self.reporting = session, reporting
        self.latest: dict[str, str] = {}
        self.cursor = session.changes.serial
        self.recheck()

    def event(self, job: Job, phase: str) -> None:
        if job.kind == "issue_check" or job.obsolete:
            return
        scope = fingerprint((job.kind, job.key, sorted(job.outputs)))
        if phase == "submitted":
            self.latest[scope] = job.id
            if self.reporting.repository.scopes.get((self.name, scope)):
                self.reporting.invalidate(self.name, scope)
        elif self.latest.get(scope) == job.id:
            self.publish(scope, job)

    def publish(self, scope: str, job: Job) -> None:
        if job.state not in ("failed", "succeeded"):
            return
        if job.state == "succeeded" and not self.reporting.repository.scopes.get(
            (self.name, scope)
        ):
            return
        ticket = self.reporting.begin(self.name, scope)
        rows = (task_issue(self.session, scope, job),) if job.state == "failed" else ()
        self.reporting.complete(ticket, rows)

    def recheck(self) -> None:
        for scope, identity in self.latest.items():
            job = self.session.scheduler.registry.by_id.get(identity)
            if job is not None:
                self.publish(scope, job)
        self.reporting.complete(self.reporting.begin(self.name, "document"), ())

    def prune(self) -> None:
        journal = self.session.changes
        if self.cursor == journal.serial:
            return
        delta = journal.since(self.cursor)
        self.cursor = journal.serial
        live = (
            self.session.document.index.entities.keys()
            | self.session.document.index.controls.keys()
        )
        removed = (delta.entities.keys() | delta.controls.keys()) - live
        for row in tuple(self.reporting.repository.records.values()):
            if row.provider == self.name and row.target in removed:
                self.reporting.remove(self.name, row.scope)
                self.latest.pop(row.scope, None)

    def reset(self) -> None:
        self.latest.clear()
        self.cursor = self.session.changes.serial
        self.recheck()


def task_issue(session: "Session", scope: str, job: Job) -> Issue:
    return Issue(
        "tasks.v1",
        scope,
        "CALCULATION_FAILED",
        job.label + " failed",
        stage=job.kind,
        severity="error",
        details=job.error,
        source=job.id,
        evidence=evidence(
            job_id=job.id, revision=job.dispatch_revision, outputs=sorted(job.outputs)
        ),
        **task_target(session, job),
    )


def task_target(session: "Session", job: Job) -> dict[str, Any]:
    live = session.document.index.entities.keys() | session.document.index.controls.keys()
    related = tuple(sorted(job.outputs & live))
    target = related[0] if related else ""
    kind = (
        "SCP" if target in session.document.index.entities else "CONTROL" if target else "DOCUMENT"
    )
    return dict(target=target, kind=kind, related=related)
