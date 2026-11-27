"""Resolve packaged worker ownership independently from development configuration."""

import json
import os
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "_runtime"
WORKER = Path("tools/runtime/skin/application_worker.py")


def installed() -> tuple[Path, Path]:
    if "__compiled__" in globals() or (PACKAGE / "build.json").is_file():
        return bundled(PACKAGE / "avbd")
    root = Path(os.environ.get("ANTHROFORGE_AVBD_RUNTIME", PACKAGE.parents[2])).resolve()
    python = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.is_file() or not (root / WORKER).is_file():
        raise ValueError(
            "AVBD runtime unavailable. Configure ANTHROFORGE_AVBD_RUNTIME for source runs."
        )
    return root, python


def bundled(root: Path) -> tuple[Path, Path]:
    try:
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        if manifest["schema"] != 1:
            raise ValueError("Unsupported AVBD bundle schema.")
        validate_files(root, ("python/python.exe", str(WORKER), *manifest["required"]))
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError(
            "Bundled AVBD runtime is incomplete. Reinstall the complete app folder."
        ) from error
    return root, root / "python/python.exe"


def validate_files(root: Path, names: tuple[str, ...]) -> None:
    for name in names:
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError(f"Missing bundled AVBD file: {name}")
