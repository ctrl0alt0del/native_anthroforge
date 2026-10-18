"""Provider/scope reconciliation retains evidence through failed or pending checks."""

from anthroforge.core.issues import CheckState, Issue


class IssueRepository:
    def __init__(self) -> None:
        self.revision = 0
        self.records: dict[str, Issue] = {}
        self.scopes: dict[tuple[str, str], dict[str, Issue]] = {}
        self.states: dict[tuple[str, str], CheckState] = {}
        self.dismissed: set[str] = set()

    def state(self, key: tuple[str, str], value: CheckState) -> None:
        if self.states.get(key) != value:
            self.states[key] = value
            self.revision += 1

    def replace(self, key: tuple[str, str], rows: tuple[Issue, ...], generation: int) -> None:
        if any((row.provider, row.scope) != key for row in rows):
            raise ValueError("A check may only replace its own provider and scope.")
        desired = {row.id: row for row in rows}
        if len(desired) != len(rows):
            raise ValueError("Duplicate issue identity within a check.")
        previous = self.scopes.get(key, {})
        for identity in previous.keys() - desired.keys():
            self.records.pop(identity, None)
            self.dismissed.discard(identity)
        self.scopes[key] = desired
        self.records.update(desired)
        self.state(key, CheckState("COMPLETE", generation))
        if previous != desired:
            self.revision += 1

    def remove(self, key: tuple[str, str]) -> None:
        for identity in self.scopes.pop(key, {}):
            self.records.pop(identity, None)
            self.dismissed.discard(identity)
        if self.states.pop(key, None) is not None:
            self.revision += 1

    def dismiss(self, identity: str, dismissed: bool = True) -> None:
        if identity not in self.records:
            raise ValueError("Issue no longer exists; refresh the report.")
        if dismissed != (identity in self.dismissed):
            self.dismissed.add(identity) if dismissed else self.dismissed.discard(identity)
            self.revision += 1

    def clear(self) -> None:
        self.records.clear()
        self.scopes.clear()
        self.states.clear()
        self.dismissed.clear()
        self.revision += 1
