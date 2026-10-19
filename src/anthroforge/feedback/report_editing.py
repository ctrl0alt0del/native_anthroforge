"""Atomic description-only archive edits preserve all other members and report identity."""

import json
import os
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from .local_inbox import details


def update_description(path: Path, description: str) -> None:
    if not description.strip():
        raise ValueError("Add a description before saving the report.")
    handle, name = tempfile.mkstemp(prefix=".afreport-edit-", dir=path.parent)
    os.close(handle)
    temporary = Path(name)
    try:
        previous = identity(path)
        rewrite(path, temporary, description.strip())
        publish(path, temporary, previous)
    finally:
        temporary.unlink(missing_ok=True)


def identity(path: Path) -> tuple[int, int, int]:
    state = path.stat()
    return state.st_ino, state.st_size, state.st_mtime_ns


def publish(path: Path, temporary: Path, previous: tuple[int, int, int]) -> None:
    with temporary.open("r+b") as stream:
        os.fsync(stream.fileno())
    if identity(path) != previous:
        raise ValueError("The report changed while saving. Reload it before editing again.")
    os.replace(temporary, path)


def rewrite(path: Path, temporary: Path, description: str) -> None:
    with ZipFile(path) as source, ZipFile(temporary, "w", ZIP_DEFLATED) as output:
        data = details(source)
        data.update(description=description, updated_at=datetime.now(UTC).isoformat())
        encoded = json.dumps(data, indent=2, allow_nan=False)
        if len(encoded.encode("utf-8")) > 2 * 1024 * 1024:
            raise ValueError("Report description exceeds the supported size limit.")
        output.writestr("report.json", encoded)
        output.writestr("description.txt", description.encode("utf-8"))
        copy_attachments(source, output)


def copy_attachments(source: ZipFile, output: ZipFile) -> None:
    output.comment = source.comment
    for item in source.infolist():
        if item.filename not in ("report.json", "description.txt"):
            with source.open(item) as reader, output.open(item, "w") as writer:
                shutil.copyfileobj(reader, writer, 256 * 1024)
