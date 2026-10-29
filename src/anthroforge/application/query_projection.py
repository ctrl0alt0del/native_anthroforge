"""Serialization of immutable query metadata, separate from retained native buffers."""

from dataclasses import fields, is_dataclass
from typing import Any


def plain(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: plain(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(item) for item in value]
    return value
