"""Atomic image/JSON archives; the isolated renderer reads only a temporary frozen package."""

import json
import os
import tempfile
import zipfile
from pathlib import Path
from threading import Event
from typing import Any

from anthroforge import __version__

from .report_renderer import render
from .storage import write_package


def check(cancel: Event) -> None:
    if cancel.is_set():
        raise ValueError("Inspection export cancelled.")


def write(path: Path, frozen: Any, metadata: dict[str, Any], cancel: Event) -> str:
    with tempfile.TemporaryDirectory(prefix="anthroforge-inspection-") as directory:
        root = Path(directory)
        check(cancel)
        write_package(root / "snapshot.anthroforge", frozen.source.document, frozen.source.assets)
        (root / "view.json").write_text(json.dumps(frozen.view), encoding="utf-8")
        render(root, frozen.source.document.revision, cancel)
        image = json.loads((root / "image.png.json").read_text(encoding="utf-8"))
        verify(image, metadata)
        metadata.update(application_version=__version__, image=image)
        archive(path, root / "image.png", metadata, cancel)
    return str(path)


def verify(image: dict[str, Any], metadata: dict[str, Any]) -> None:
    if not image["captured"] or image["revision"] != metadata["revision"]:
        raise ValueError("Renderer did not capture the declared revision.")
    if image.get("inspection_view") != metadata["view"]:
        raise ValueError("Renderer view does not match the report snapshot.")
    image.pop("image", None)  # Do not publish temporary paths.


def archive(path: Path, image: Path, metadata: dict[str, Any], cancel: Event) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=".afinspection-", dir=path.parent)
    os.close(descriptor)
    try:
        check(cancel)
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as target:
            target.writestr("inspection.json", json.dumps(metadata, indent=2, allow_nan=False))
            target.write(image, "image.png")
        check(cancel)
        with open(temporary, "r+b") as stream:
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
