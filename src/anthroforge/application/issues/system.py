"""Session composition; diagnostics never become authored document state."""

from collections.abc import Callable
from functools import partial
from typing import TYPE_CHECKING

from . import fiber_collisions, formulas, mirroring, providers, repairs, tissue_geometry
from .listening import Listening
from .presentation import Presentation
from .reporting import Reporting
from .repository import IssueRepository
from .resolution import Resolution
from .task_reports import TaskReports

if TYPE_CHECKING:
    from ..coordinator import TaskCoordinator
    from ..session import Session


class IssueSystem:
    def __init__(self, session: "Session") -> None:
        self.session = session
        self.repository = IssueRepository()
        self.reporting = Reporting(self.repository)
        self.presentation = Presentation(self.repository)
        self.listening = Listening(session, self.reporting)
        self.tasks = TaskReports(session, self.reporting)
        self.resolution = Resolution(self.repository, self.recheck)
        self.register_providers(session)
        self.attach(session.scheduler)

    def register_providers(self, session: "Session") -> None:
        for provider in (
            *providers.builtins(),
            formulas.provider(),
            mirroring.provider(session),
            fiber_collisions.provider(session),
            tissue_geometry.provider(session),
        ):
            self.listening.register(provider)

    def attach(self, scheduler: "TaskCoordinator") -> None:
        scheduler.service_tick = self.session.synchronize_services
        scheduler.lifecycle = self.tasks.event

    def synchronize(self) -> None:
        self.tasks.prune()
        self.listening.synchronize()
        if not self.listening.closed:
            repairs.tick(self.session)

    def recheck(self, provider: str | None = None) -> None:
        handlers: dict[str, Callable[[], None]] = {
            name: partial(self.listening.recheck, name) for name in self.listening.providers
        }
        handlers[self.tasks.name] = self.tasks.recheck
        if provider is not None and provider not in handlers:
            raise ValueError("The issue detector is unavailable.")
        for name, callback in handlers.items():
            if provider is None or name == provider:
                callback()

    def reset(self) -> None:
        self.listening.cancel()
        self.reporting.reset()
        self.resolution.running.clear()
        self.listening.reset()
        self.tasks.reset()
        self.attach(self.session.scheduler)

    def close(self) -> None:
        self.listening.closed = True
        self.listening.cancel()
