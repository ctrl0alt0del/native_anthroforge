"""Pinned external remesher assets; never search Blender or substitute another backend."""

import hashlib
import json
import platform
from pathlib import Path
from typing import Any, cast

PACKAGE = Path(__file__).resolve().parents[1]


def location() -> Path:
    packaged = PACKAGE / "_runtime/quadwild"
    return packaged if packaged.is_dir() else PACKAGE.parents[1] / ".tools/quadwild"


def manifest() -> dict[str, Any]:
    return cast(
        dict[str, Any], json.loads((PACKAGE / "data/quadwild.json").read_text(encoding="utf-8"))
    )


def verify(root: Path | None = None) -> Path:
    metadata, folder = manifest(), (root or location()).resolve()
    if platform.system() != metadata["platform"] or platform.machine().upper() != "AMD64":
        raise ValueError("This QuadWild bundle is qualified only for Windows x64.")
    for name, expected in metadata["files"].items():
        path = (folder / name).resolve()
        if not path.is_relative_to(folder) or not path.is_file():
            raise ValueError(f"Missing QuadWild asset: {name}. Run tools/setup_quadwild.py.")
        with path.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != expected:
            raise ValueError(f"QuadWild asset fingerprint mismatch: {name}.")
    return folder
