"""Generation and epoch guarded check transactions and direct producer reports."""

from anthroforge.core.issues import Check, CheckState, Issue

from .repository import IssueRepository


class Reporting:
    def __init__(self, repository: IssueRepository) -> None:
        self.repository = repository
        self.epoch = 0
        self.generations: dict[tuple[str, str], int] = {}

    def begin(self, provider: str, scope: str, status: str = "CHECKING") -> Check:
        key = provider, scope
        generation = self.generations.get(key, 0) + 1
        self.generations[key] = generation
        self.repository.state(key, CheckState(status, generation))
        return Check(provider, scope, generation, self.epoch)

    def current(self, check: Check) -> bool:
        return (
            check.epoch == self.epoch
            and self.generations.get((check.provider, check.scope)) == check.generation
        )

    def complete(self, check: Check, rows: tuple[Issue, ...]) -> bool:
        if not self.current(check):
            return False
        self.repository.replace((check.provider, check.scope), rows, check.generation)
        return True

    def fail(self, check: Check, error: str, cancelled: bool = False) -> bool:
        if not self.current(check):
            return False
        state = CheckState("CANCELLED" if cancelled else "FAILED", check.generation, error)
        self.repository.state((check.provider, check.scope), state)
        return True

    def report(self, issue: Issue) -> None:
        key = issue.provider, issue.scope
        prior = self.repository.scopes.get(key, {})
        rows = tuple(row for row in prior.values() if semantic_key(row) != semantic_key(issue)) + (
            issue,
        )
        self.complete(self.begin(*key), rows)

    def invalidate(self, provider: str, scope: str) -> None:
        self.begin(provider, scope, "PENDING")

    def remove(self, provider: str, scope: str) -> None:
        key = provider, scope
        self.generations[key] = self.generations.get(key, 0) + 1
        self.repository.remove(key)

    def reset(self) -> None:
        self.epoch += 1
        self.generations.clear()
        self.repository.clear()


def semantic_key(issue: Issue) -> tuple[str, ...]:
    return issue.provider, issue.scope, issue.stage, issue.code, issue.local_key
