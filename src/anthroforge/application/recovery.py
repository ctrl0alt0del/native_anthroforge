"""Owned recovery packages with metadata, atomic writes and per-project retention."""

import hashlib
import json
import os
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from threading import Event
from typing import Any
from uuid import uuid4

from anthroforge.core.document import Document

from .resources import Resources
from .storage import FileLock, atomic_save

KEEP = 3


def metadata(document: Document, origin: str) -> dict[str, Any]:
    identity = str(document.id) + os.path.normcase(origin)
    return dict(
        schema=1,
        group=hashlib.sha256(identity.encode()).hexdigest()[:24],
        name=document.name,
        origin=origin,
        revision=document.revision,
        created=datetime.now(UTC).isoformat(),
    )


def inspect(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        entry = archive.getinfo("recovery.json")
        if entry.file_size > 65536:
            raise ValueError("Recovery metadata is too large.")
        data = json.loads(archive.read(entry))
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise ValueError("Unsupported recovery metadata.")
    if any(not isinstance(data.get(key), str) for key in ("group", "name", "origin", "created")):
        raise ValueError("Invalid recovery metadata.")
    return {**data, "path": str(path.resolve())}


class RecoveryStore:
    def __init__(self, directory: Path) -> None:
        self.directory = directory.resolve()

    def owns(self, path: Path) -> bool:
        return path.resolve().parent == self.directory and path.name.startswith("autosave-")

    def scan(self) -> tuple[list[dict[str, Any]], int]:
        rows, unreadable = [], 0
        for path in self.directory.glob("autosave-*.anthroforge"):
            try:
                rows.append(inspect(path))
            except (OSError, ValueError, KeyError, zipfile.BadZipFile):
                unreadable += 1
        return sorted(rows, key=lambda row: row["created"], reverse=True), unreadable

    def write(
        self, document: Document, resources: Resources, origin: str, cancel: Event
    ) -> dict[str, Any]:
        self.directory.mkdir(parents=True, exist_ok=True)
        info = metadata(document, origin)
        path = self.directory / f"autosave-{info['group']}-{uuid4().hex}.anthroforge"
        atomic_save(path, document, resources, cancel, info)
        warning = self.prune(info["group"])
        return {**info, "path": str(path), "warning": warning}

    def prune(self, group: str) -> str:
        rows, _ = self.scan()
        expired = [row for row in rows if row["group"] == group][KEEP:]
        failures = 0
        for row in expired:
            try:
                self.remove(Path(row["path"]))
            except (OSError, ValueError):
                failures += 1
        return f"Could not remove {failures} older recovery copies." if failures else ""

    def remove(self, path: Path) -> None:
        if not self.owns(path):
            raise ValueError("This file is not an owned recovery copy.")
        lock = FileLock(path)
        try:
            path.unlink()
        finally:
            lock.close()
        Path(str(path) + ".lock").unlink(missing_ok=True)
