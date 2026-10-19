"""Read/delete capability is separate from delivery; keys are opaque to the UI."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ReportEntry:
    key: str
    title: str
    category: str = ""
    created_at: str = ""
    error: str = ""


@dataclass(frozen=True)
class ReportDetail:
    entry: ReportEntry
    description: str
    annotated_png: bytes
    location: str


class ReportInbox(Protocol):
    def entries(self) -> tuple[ReportEntry, ...]:
        """Return current reports, newest first; no screenshot payloads."""
        ...

    def read(self, key: str) -> ReportDetail:
        """Load one report; a missing or unreadable report raises an exception."""
        ...

    def delete(self, key: str) -> None:
        """Delete exactly the selected report; a missing report is already deleted."""
        ...

    def update_description(self, key: str, description: str) -> None:
        """Atomically replace description text; preserve identity, screenshots and metadata."""
        ...
