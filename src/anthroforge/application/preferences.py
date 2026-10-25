"""Version-independent user preferences with atomic persistence and explicit injection."""

import json
import os
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

from anthroforge.core.preferences import Preferences

from . import user_json


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
    user_json.write(path, {"schema": 1, "values": asdict(value)})


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
