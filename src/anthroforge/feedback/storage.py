"""Atomic, idempotent local inbox; no dependency on the installation directory."""

import json
import os
import tempfile
from pathlib import Path
from uuid import UUID
from zipfile import ZIP_DEFLATED, ZipFile

from .records import Receipt, Report, images, metadata


def default_directory() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
    return base / "AnthroForge" / "Reports"


class LocalReportConsumer:
    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory if directory is not None else default_directory()

    @property
    def description(self) -> str:
        return "Local report inbox: " + str(self.directory)

    def submit(self, report: Report) -> Receipt:
        if UUID(report.id).hex != report.id:
            raise ValueError("Invalid report identity.")
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.directory / f"{report.id}.afreport.zip"
        publish(path, report)
        return Receipt(str(path), self.directory.resolve().as_uri())


def publish(path: Path, report: Report) -> None:
    handle, name = tempfile.mkstemp(prefix=".afreport-", dir=path.parent)
    os.close(handle)
    temporary = Path(name)
    try:
        archive(temporary, report)
        try:
            os.link(temporary, path)  # Atomic publication without overwriting another report.
        except FileExistsError:
            verify_existing(path, report)
    finally:
        temporary.unlink(missing_ok=True)


def archive(path: Path, report: Report) -> None:
    with ZipFile(path, "w", ZIP_DEFLATED) as output:
        output.writestr("report.json", json.dumps(metadata(report), indent=2, allow_nan=False))
        output.writestr("description.txt", report.description.encode("utf-8"))
        for name, data in images(report).items():
            output.writestr(name, data)
    with path.open("r+b") as stream:
        os.fsync(stream.fileno())


def verify_existing(path: Path, report: Report) -> None:
    with ZipFile(path) as existing:
        matches = json.loads(existing.read("report.json")) == metadata(report)
        matches &= all(existing.read(name) == data for name, data in images(report).items())
        matches &= existing.read("description.txt").decode("utf-8") == report.description
    if not matches:
        raise ValueError("A different report already uses this identity; nothing was overwritten.")
