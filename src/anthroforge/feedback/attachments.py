"""Owned file attachments stream through any report consumer without anatomy dependencies."""

import hashlib
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO


@dataclass(frozen=True)
class FileAttachment:
    name: str
    path: Path
    checksum: str
    owner: Any = field(default=None, repr=False, compare=False)

    def open(self) -> BinaryIO:
        return self.path.open("rb")


def materialize(name: str, writer: Any) -> FileAttachment:
    if Path(name).name != name or name in (
        "report.json",
        "description.txt",
        "original.png",
        "annotated.png",
    ):
        raise ValueError("Invalid report attachment name.")
    owner = tempfile.TemporaryDirectory(prefix="anthroforge-feedback-")
    path = Path(owner.name) / name
    writer(path)
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return FileAttachment(name, path, digest, owner)


def write(archive: Any, attachment: FileAttachment) -> None:
    with (
        attachment.open() as source,
        archive.open(attachment.name, "w", force_zip64=True) as output,
    ):
        while block := source.read(1024 * 1024):
            output.write(block)


def verify(archive: Any, attachment: FileAttachment) -> bool:
    with archive.open(attachment.name) as source:
        return hashlib.file_digest(source, "sha256").hexdigest() == attachment.checksum
