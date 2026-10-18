"""Batched read-only checks submitted to the application's task coordinator."""

from dataclasses import dataclass
from functools import partial
from threading import Event
from typing import TYPE_CHECKING, Any

from anthroforge.core.document import Document
from anthroforge.core.issues import Check, Issue
from anthroforge.core.jobs import Job
from anthroforge.core.scheduling import Workload

from .providers import Provider

if TYPE_CHECKING:
    from .listening import Listening


@dataclass(frozen=True)
class Input:
    document: Document
    checks: tuple[Check, ...]
    sources: tuple[Any, ...]


def make_job(listener: "Listening", provider: Provider, scopes: set[str]) -> Job:
    job = Job(
        "Check " + provider.name,
        frozenset(),
        partial(prepare, listener, provider, scopes),
        partial(compute, provider),
        partial(publish, listener, provider),
        key="issues:" + provider.name,
        kind="issue_check",
        writes=False,
        priority=-10,
        publish_during_edit=True,
    )
    configure(job, listener, provider.name, scopes)
    return job


def configure(job: Job, listener: "Listening", provider: str, scopes: set[str]) -> None:
    job.workload = lambda _: Workload(affected=len(scopes))
    job.cleanup = partial(finished, listener, provider, job)
    job.retry = partial(listener.recheck, provider)
    listener.tickets[provider] = tuple(
        listener.reporting.begin(provider, s, "PENDING") for s in scopes
    )


def prepare(
    listener: "Listening", provider: Provider, scopes: set[str], document: Document
) -> Input:
    selected = sorted(scopes & provider.scopes(document))
    checks = tuple(listener.reporting.begin(provider.name, scope) for scope in selected)
    listener.tickets[provider.name] = checks
    return Input(document, checks, tuple(provider.source(document, s) for s in selected))


def compute(
    provider: Provider, captured: Input, cancel: Event
) -> tuple[Input, tuple[tuple[Issue, ...], ...]]:
    rows = []
    for check in captured.checks:
        if cancel.is_set():
            break
        rows.append(provider.check(captured.document, check.scope, cancel))
    return captured, tuple(rows)


def publish(listener: "Listening", provider: Provider, payload: Any) -> None:
    captured, rows = payload
    document = listener.session.document
    for check, source, result in zip(captured.checks, captured.sources, rows, strict=True):
        if source == provider.source(document, check.scope):
            listener.reporting.complete(check, result)
        elif check.scope in provider.scopes(document):
            listener.invalidate(provider.name, {check.scope})


def finished(listener: "Listening", provider: str, job: Job, state: str) -> None:
    if state in ("failed", "cancelled", "obsolete"):
        for ticket in listener.tickets.get(provider, ()):
            listener.reporting.fail(ticket, job.error or "Check cancelled", state != "failed")
    listener.running.pop(provider, None)
    listener.tickets.pop(provider, None)
