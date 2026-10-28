"""Owned immutable package snapshot; inspecting never adopts or recalculates the source."""

import hashlib
import json
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from anthroforge.core.document import Document

from .storage import FORMAT, READ_VERSIONS, decode_document


@dataclass(frozen=True)
class Source:
    directory: Any
    path: Path
    original: str
    digest: str
    document: Document
    metadata: dict[str, Any]


def inspect(path: str, cancel: Any) -> Source:
    original = Path(path).resolve(strict=True)
    directory = tempfile.TemporaryDirectory(prefix="anthroforge-assembly-")
    target = Path(directory.name) / "source.anthroforge"
    try:
        digest = snapshot(original, target, cancel)
        with zipfile.ZipFile(target) as archive:
            data = json.loads(archive.read("manifest.json"))
        require_format(data)
        document = decode_document(data["document"])
        return Source(directory, target, str(original), digest, document, data)
    except Exception:
        directory.cleanup()
        raise


def require_format(data: Any) -> None:
    if data.get("format") != FORMAT or data.get("version") not in READ_VERSIONS:
        raise ValueError("Unsupported AnthroForge project format/version.")


def snapshot(source: Path, target: Path, cancel: Any) -> str:
    digest = hashlib.sha256()
    with source.open("rb") as incoming, target.open("xb") as output:
        while chunk := incoming.read(1024 * 1024):
            cancelled(cancel)
            digest.update(chunk)
            output.write(chunk)
    return digest.hexdigest()


def cancelled(cancel: Any) -> None:
    if cancel.is_set():
        raise ValueError("Anatomy import cancelled.")
