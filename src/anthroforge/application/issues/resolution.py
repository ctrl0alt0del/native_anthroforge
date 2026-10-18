"""Explicit registered repairs, followed by a new provider verification."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from anthroforge.core.issues import Issue

from .repository import IssueRepository

TERMINAL = frozenset(("DONE", "FAILED", "CANCELLED", "UNRESOLVED"))


@dataclass(frozen=True)
class Solver:
    name: str
    label: str
    codes: tuple[str, ...]
    applicable: Callable[[Issue], bool]
    invoke: Callable[[Issue], tuple[str, ...]]


@dataclass
class Repair:
    issue: Issue
    solver: str
    jobs: tuple[str, ...]
    state: str = "REQUESTED"
    error: str = ""
    generation: int = 0
    outputs: dict[str, Any] = field(default_factory=dict)


class Resolution:
    def __init__(self, repository: IssueRepository, recheck: Callable[[str], None]) -> None:
        self.repository, self.recheck = repository, recheck
        self.solvers: dict[str, Solver] = {}
        self.running: dict[str, Repair] = {}

    def register(self, solver: Solver) -> None:
        if solver.name in self.solvers:
            raise ValueError("Duplicate issue solver.")
        self.solvers[solver.name] = solver

    def available(self, issue: Issue) -> tuple[Solver, ...]:
        state = self.repository.states.get((issue.provider, issue.scope))
        if state is None or state.status != "COMPLETE":
            return ()
        return tuple(
            value
            for value in self.solvers.values()
            if issue.code in value.codes and value.applicable(issue)
        )

    def invoke(self, identity: str, name: str) -> Repair:
        issue = self.repository.records.get(identity)
        solver = self.solvers.get(name)
        existing = self.running.get(identity)
        if existing is not None and existing.state not in TERMINAL:
            raise ValueError("A repair is already active for this issue.")
        if issue is None or solver not in self.available(issue):
            raise ValueError("Issue is stale or this repair is not applicable; recheck first.")
        assert solver is not None
        repair = Repair(issue, name, solver.invoke(issue))
        self.running[identity] = repair
        self.repository.revision += 1
        return repair

    def verify(self, repair: Repair) -> None:
        key = repair.issue.provider, repair.issue.scope
        state = self.repository.states.get(key)
        repair.generation = state.generation if state else 0
        repair.state = "VERIFYING"
        self.recheck(repair.issue.provider)
        self.repository.revision += 1

    def verified(self, repair: Repair) -> None:
        issue = repair.issue
        state = self.repository.states.get((issue.provider, issue.scope))
        if state and state.generation > repair.generation and state.status == "COMPLETE":
            remains = any(
                row.code == issue.code and row.target == issue.target
                for row in self.repository.scopes.get((issue.provider, issue.scope), {}).values()
            )
            self.finish(repair, "UNRESOLVED" if remains else "DONE")
        elif state and state.status in ("FAILED", "CANCELLED"):
            self.finish(repair, "FAILED", state.error or "Verification did not complete.")
        elif state is None:
            self.finish(repair, "CANCELLED", "Issue scope was removed before verification.")

    def finish(self, repair: Repair, state: str, error: str = "") -> None:
        repair.state, repair.error = state, error
        self.repository.revision += 1
