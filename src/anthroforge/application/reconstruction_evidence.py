"""Immutable embedded evidence, never interpreted as executable project instructions."""

import hashlib
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any
from uuid import uuid4

from anthroforge.core.reconstruction import ReviewEvidence

from . import reconstruction_imports
from . import reconstruction_state as records

FORMATS = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".afinspection.zip": "application/afinspection",
    ".afprofile.zip": "application/afprofile",
}


def import_file(session: Any, path: str) -> Any:
    source = Path(path)
    media = next((v for k, v in FORMATS.items() if source.name.lower().endswith(k)), "")
    if not media:
        raise ValueError("Choose PNG/JPEG, an inspection report or a performance report.")
    row = ReviewEvidence(source.name, str(uuid4()), "", media)
    return reconstruction_imports.start(session, path, "evidence", row, load)


def load(path: Path, row: Any, cancel: Any) -> Any:
    chunks = []
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            if cancel.is_set():
                raise ValueError("Evidence import cancelled.")
            chunks.append(chunk)
    data = b"".join(chunks)
    return replace(row, digest=hashlib.sha256(data).hexdigest()), row.resource, data


def remove(session: Any, evidence: str) -> None:
    if any(evidence in row.evidence for row in records.state(session).reviews):
        raise ValueError("This evidence is referenced by a recorded review.")
    records.remove(session, "evidence", evidence)


def export(session: Any, evidence: str, path: str) -> None:
    row = records.selected(session, "evidence", evidence)
    data = session.resources.evidence[row.resource]
    if hashlib.sha256(data).hexdigest() != row.digest:
        raise ValueError("Evidence checksum mismatch.")
    with Path(path).open("xb") as stream:
        stream.write(data)


def inspect(session: Any) -> Any:
    return dict(evidence=[asdict(row) for row in records.state(session).evidence])


def verify(document: Any, resources: Any) -> None:
    for row in document.reconstruction.evidence:
        if hashlib.sha256(resources.evidence[row.resource]).hexdigest() != row.digest:
            raise ValueError("Embedded review evidence checksum mismatch: " + row.name)


def execute(session: Any, operation: str, arguments: Any) -> Any:
    commands: dict[str, Any] = dict(
        import_file=import_file, inspect=inspect, remove=remove, export=export
    )
    name = operation.removeprefix("reconstruction.evidence.")
    if name not in commands:
        raise ValueError("Unknown evidence operation.")
    return commands[name](session, **arguments)
