"""Opaque immutable builder records; algorithms own their parameter schemas."""

import json
from dataclasses import dataclass, replace
from typing import Any


@dataclass(frozen=True, slots=True)
class BuilderConfiguration:
    builder: str
    parameters: str = "{}"

    def __post_init__(self) -> None:
        if not isinstance(self.builder, str) or not self.builder.strip():
            raise ValueError("A draft builder needs an identifier.")
        data = json.loads(self.parameters)
        if not isinstance(data, dict):
            raise ValueError("Builder parameters must be an object.")
        encoded = json.dumps(data, sort_keys=True, allow_nan=False, separators=(",", ":"))
        object.__setattr__(self, "parameters", encoded)

    def values(self) -> dict[str, Any]:
        return dict(json.loads(self.parameters))


@dataclass(frozen=True, slots=True)
class DraftSettings:
    backend: str = "FIELD"
    configurations: tuple[BuilderConfiguration, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.backend, str) or not self.backend.strip():
            raise ValueError("A draft builder needs an identifier.")
        if len({row.builder for row in self.configurations}) != len(self.configurations):
            raise ValueError("Builder configurations must have unique identifiers.")

    def configuration(self, builder: str = "") -> BuilderConfiguration:
        key = builder or self.backend
        return next((r for r in self.configurations if r.builder == key), BuilderConfiguration(key))

    def updated(self, value: BuilderConfiguration) -> "DraftSettings":
        rows = {r.builder: r for r in self.configurations} | {value.builder: value}
        return replace(self, configurations=tuple(rows[key] for key in sorted(rows)))


@dataclass(frozen=True, slots=True)
class AppliedDraftConfiguration:
    configuration: BuilderConfiguration
    builder_version: int


def configuration(builder: str, values: dict[str, Any]) -> BuilderConfiguration:
    return BuilderConfiguration(builder, json.dumps(values, allow_nan=False))
