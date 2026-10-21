"""Change-driven detectors; no timers, worker pools, or geometry writes of their own."""

from typing import TYPE_CHECKING

from anthroforge.core.issues import Check
from anthroforge.core.jobs import Job

from ..changes import DocumentChanges
from . import checking
from .providers import Provider
from .reporting import Reporting

if TYPE_CHECKING:
    from ..session import Session


class Listening:
    def __init__(self, session: "Session", reporting: Reporting) -> None:
        self.session, self.reporting = session, reporting
        self.providers: dict[str, Provider] = {}
        self.pending: dict[str, set[str]] = {}
        self.running: dict[str, Job] = {}
        self.tickets: dict[str, tuple[Check, ...]] = {}
        self.cursor = -1
        self.closed = False

    def register(self, provider: Provider) -> None:
        if provider.name in self.providers:
            raise ValueError("Duplicate issue provider.")
        self.providers[provider.name] = provider
        if provider.automatic:
            self.recheck(provider.name)

    def unregister(self, name: str) -> None:
        self.require(name)
        self.cancel(name)
        del self.providers[name]
        for provider, scope in tuple(self.reporting.repository.states):
            if provider == name:
                self.reporting.remove(provider, scope)

    def require(self, name: str) -> Provider:
        if name not in self.providers:
            raise ValueError("The issue detector is unavailable.")
        return self.providers[name]

    def invalidate(self, name: str, scopes: set[str]) -> None:
        pending = self.pending.setdefault(name, set())
        for scope in scopes - pending:
            self.reporting.invalidate(name, scope)
        pending.update(scopes)

    def recheck(self, provider: str | None = None) -> None:
        selected = (self.require(provider),) if provider else tuple(self.providers.values())
        for value in selected:
            self.discover(value, None, requested=True)

    def synchronize(self) -> None:
        if self.closed:
            return
        self.discover_changes()
        if self.session.history.before is not None:
            return
        for name, scopes in tuple(self.pending.items()):
            if scopes and name not in self.running:
                job = checking.make_job(self, self.providers[name], scopes)
                self.pending[name] = set()
                self.running[name] = job
                self.session.scheduler.submit(job)

    def discover_changes(self) -> None:
        journal = self.session.changes
        if self.cursor == journal.serial:
            return
        delta = journal.since(self.cursor)
        self.cursor = journal.serial
        for provider in self.providers.values():
            self.discover(provider, delta)

    def discover(self, provider: Provider, delta: DocumentChanges | None, requested: bool = False) -> None:
        try:
            self.update_scopes(provider, delta, requested)
            if (provider.name, "@provider") in self.reporting.repository.states:
                self.reporting.remove(provider.name, "@provider")
        except Exception as error:
            ticket = self.reporting.begin(provider.name, "@provider")
            self.reporting.fail(ticket, str(error) or type(error).__name__)

    def update_scopes(self, provider: Provider, delta: DocumentChanges | None, requested: bool = False) -> None:
        live = provider.scopes(self.session.document)
        scopes = (
            live
            if delta is None or delta.reset
            else provider.affected(self.session.document, delta)
        )
        if requested:
            self.invalidate(provider.name, scopes & live)
        else:
            self.mark_changed(provider, scopes & live)
        self.remove_absent(provider.name, live)

    def mark_changed(self, provider: Provider, scopes: set[str]) -> None:
        if provider.automatic:
            self.invalidate(provider.name, scopes)
            return
        known = self.reporting.repository.states
        for scope in scopes:
            if (provider.name, scope) in known:
                self.reporting.invalidate(provider.name, scope)

    def remove_absent(self, name: str, live: set[str]) -> None:
        self.pending.setdefault(name, set()).intersection_update(live)
        for provider, scope in tuple(self.reporting.repository.states):
            if provider == name and scope not in live and scope != "@provider":
                self.reporting.remove(provider, scope)

    def cancel(self, provider: str | None = None) -> None:
        selected = (self.require(provider).name,) if provider else tuple(self.providers)
        for name in selected:
            for scope in self.pending.pop(name, set()):
                ticket = self.reporting.begin(name, scope)
                self.reporting.fail(ticket, "Check cancelled", cancelled=True)
            job = self.running.get(name)
            if job and job.active:
                self.session.scheduler.cancel_job(job.id)

    def reset(self) -> None:
        self.pending.clear()
        self.running.clear()
        self.tickets.clear()
        self.cursor = -1
        self.closed = False
        for provider in self.providers.values():
            if provider.automatic:
                self.recheck(provider.name)
