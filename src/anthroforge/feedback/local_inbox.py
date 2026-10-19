"""Bounded archive reads and scoped deletion for the version-independent local inbox."""

import json
from pathlib import Path
from typing import Any
from zipfile import ZipFile

from .inbox import ReportDetail, ReportEntry
from .storage import default_directory


class LocalReportInbox:
    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory if directory is not None else default_directory()

    def entries(self) -> tuple[ReportEntry, ...]:
        if not self.directory.exists():
            return ()
        rows = [
            entry(path)
            for path in self.directory.iterdir()
            if path.name.endswith(".afreport.zip") and path.is_file() and not path.is_symlink()
        ]
        return tuple(sorted(rows, key=lambda row: (row.created_at, row.key), reverse=True))

    def path(self, key: str) -> Path:
        path = self.directory / key
        if (
            Path(key).name != key
            or not key.endswith(".afreport.zip")
            or path.is_symlink()
            or path.resolve().parent != self.directory.resolve()
        ):
            raise ValueError("Select a report in this inbox.")
        return path

    def read(self, key: str) -> ReportDetail:
        path = self.path(key)
        with ZipFile(path) as archive:
            data = details(archive)
            image = bounded_read(archive, "annotated.png", 64 * 1024 * 1024)
        return ReportDetail(summary(path.name, data), data["description"], image, str(path))

    def delete(self, key: str) -> None:
        self.path(key).unlink(missing_ok=True)


def bounded_read(archive: ZipFile, name: str, limit: int) -> bytes:
    if archive.getinfo(name).file_size > limit:
        raise ValueError(f"Report {name} exceeds the preview size limit.")
    return archive.read(name)


def details(archive: ZipFile) -> dict[str, Any]:
    data = json.loads(bounded_read(archive, "report.json", 2 * 1024 * 1024))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Unsupported report format.")
    for name in ("description", "created_at", "category"):
        if not isinstance(data.get(name), str):
            raise ValueError(f"Report is missing {name}.")
    return data


def summary(key: str, data: dict[str, Any]) -> ReportEntry:
    title = " ".join(data["description"].split())[:140] or "Untitled report"
    return ReportEntry(key, title, data["category"], data["created_at"])


def entry(path: Path) -> ReportEntry:
    try:
        with ZipFile(path) as archive:
            return summary(path.name, details(archive))
    except Exception as error:
        return ReportEntry(path.name, path.name, error=str(error) or type(error).__name__)
