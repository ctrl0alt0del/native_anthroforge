"""Read-only query projection; drawing and querying never execute a detector or fix."""

import json
from dataclasses import asdict
from typing import Any

from anthroforge.core.issues import CheckState, Issue

from .repository import IssueRepository

FILTERS = frozenset(("provider", "scope", "target", "kind", "stage", "severity", "code"))


class Presentation:
    def __init__(self, repository: IssueRepository) -> None:
        self.repository = repository

    def serialize(self, row: Issue) -> dict[str, Any]:
        state = self.repository.states.get((row.provider, row.scope), CheckState())
        return dict(
            asdict(row),
            id=row.id,
            evidence=json.loads(row.evidence),
            freshness="current" if state.status == "COMPLETE" else "stale",
            check_state=state.status,
            dismissed=row.id in self.repository.dismissed,
        )

    def get(self, identity: str) -> dict[str, Any]:
        if identity not in self.repository.records:
            raise ValueError("Issue no longer exists; refresh the report.")
        return self.serialize(self.repository.records[identity])

    def query(
        self,
        filters: dict[str, str] | None = None,
        text: str = "",
        offset: int = 0,
        limit: int = 100,
        include_dismissed: bool = False,
    ) -> dict[str, Any]:
        rows = self.filtered(filters or {}, text, include_dismissed)
        start, count = max(0, offset), min(200, max(0, limit))
        return dict(total=len(rows), records=rows[start : start + count], **self.status())

    def filtered(self, filters: dict[str, str], text: str, dismissed: bool) -> list[dict[str, Any]]:
        if filters.keys() - FILTERS:
            raise ValueError("Unknown issue filter.")
        rows = [
            self.serialize(row)
            for row in self.repository.records.values()
            if matches(row, filters) and (dismissed or row.id not in self.repository.dismissed)
        ]
        rows = [row for row in rows if text.casefold() in json.dumps(row).casefold()]
        return sorted(
            rows, key=lambda r: (severity_order(r["severity"]), r["target"], r["code"], r["id"])
        )

    def status(self) -> dict[str, Any]:
        states = self.repository.states
        complete = bool(states) and all(value.status == "COMPLETE" for value in states.values())
        return dict(
            repository_revision=self.repository.revision,
            complete=complete,
            clean=complete and not self.repository.records,
            issue_count=len(self.repository.records),
            dismissed=len(self.repository.dismissed),
            checks=[
                dict(provider=key[0], scope=key[1], **asdict(value))
                for key, value in sorted(states.items())
            ],
        )


def matches(row: Issue, filters: dict[str, str]) -> bool:
    return all(getattr(row, name) == value for name, value in filters.items())


def severity_order(severity: str) -> int:
    return ("error", "warning", "info").index(severity)
