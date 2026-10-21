"""Version-independent user preferences with atomic persistence and explicit injection."""

import json
import os
import tempfile
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

from anthroforge.core.preferences import Preferences


def user_path() -> Path:
    override = os.environ.get("ANTHROFORGE_PREFERENCES_PATH")
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
    return Path(override) if override else base / "AnthroForge" / "preferences.json"


def read(path: Path) -> Preferences:
    if not path.exists():
        return Preferences()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise ValueError("Unsupported preferences format.")
    return Preferences(**data["values"])


def write(path: Path, value: Preferences) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps({"schema": 1, "values": asdict(value)}, indent=2) + "\n"
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


class PreferenceStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path, self.value, self.error = path, Preferences(), ""
        if path is not None:
            try:
                self.value = read(path)
            except (OSError, ValueError, KeyError, TypeError) as error:
                self.error = f"Cannot load preferences: {error} ({path})"

    def update(self, **values: Any) -> dict[str, Any]:
        candidate = replace(self.value, **values)
        if self.error:
            raise ValueError(self.error + ". Correct or remove the file before saving preferences.")
        if self.path is not None:
            write(self.path, candidate)
        self.value = candidate
        return self.describe()

    def describe(self) -> dict[str, Any]:
        return {**asdict(self.value), "path": str(self.path or ""), "error": self.error}


def load_user_preferences() -> PreferenceStore:
    return PreferenceStore(user_path())
