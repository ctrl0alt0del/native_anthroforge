"""Bounded recent-project history, separate from documents and user preferences."""

import json
import os
from pathlib import Path

from . import user_json

LIMIT = 20


def canonical(path: str | Path) -> str:
    return str(Path(path).expanduser().resolve())


def unique(paths: list[str]) -> tuple[str, ...]:
    result: dict[str, str] = {}
    for path in paths:
        normalized = canonical(path)
        result.setdefault(os.path.normcase(normalized), normalized)
    return tuple(result.values())[:LIMIT]


def read(path: Path) -> tuple[str, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise ValueError("Unsupported recent-project history format.")
    values = data.get("projects")
    if not isinstance(values, list) or any(not isinstance(p, str) or not p for p in values):
        raise ValueError("Recent-project history must contain file paths.")
    return unique(values)


class RecentProjects:
    def __init__(self, path: Path | None = None) -> None:
        self.path, self.error = path, ""
        self.entries: tuple[str, ...] = ()
        if path is not None and path.exists():
            try:
                self.entries = read(path)
            except (OSError, ValueError, TypeError) as error:
                self.error = f"Cannot load recent projects: {error}"

    def remember(self, path: str | Path) -> None:
        if self.error:
            raise ValueError(self.error + ". Clear recent projects to reset the list.")
        self.replace(unique([canonical(path), *self.entries]))

    def clear(self) -> None:
        self.replace(())
        self.error = ""

    def replace(self, entries: tuple[str, ...]) -> None:
        if self.path is not None:
            user_json.write(self.path, {"schema": 1, "projects": entries})
        self.entries = entries

    def rows(self) -> list[dict[str, str]]:
        return [
            dict(path=p, name=Path(p).stem, directory=str(Path(p).parent)) for p in self.entries
        ]
