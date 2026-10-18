"""Immutable issue evidence, independent of UI, scheduling and authored documents."""

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import Any


def fingerprint(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class Issue:
    provider: str
    scope: str
    code: str
    summary: str
    target: str = ""
    kind: str = "DOCUMENT"
    stage: str = ""
    severity: str = "warning"
    details: str = ""
    source: str = ""
    related: tuple[str, ...] = ()
    evidence: str = "{}"
    local_key: str = ""

    def __post_init__(self) -> None:
        if not self.provider or not self.scope or not self.code or not self.summary:
            raise ValueError("Issues require provider, scope, code and summary.")
        if self.severity not in ("error", "warning", "info"):
            raise ValueError("Unknown issue severity.")
        if not isinstance(json.loads(self.evidence), dict):
            raise ValueError("Issue evidence must be a JSON object.")
        object.__setattr__(self, "related", tuple(self.related))

    @property
    def id(self) -> str:
        return fingerprint(
            (self.provider, self.scope, self.stage, self.code, self.local_key, self.source)
        )


@dataclass(frozen=True, slots=True)
class Check:
    provider: str
    scope: str
    generation: int
    epoch: int


@dataclass(frozen=True, slots=True)
class CheckState:
    status: str = "UNSCANNED"
    generation: int = 0
    error: str = ""


def evidence(**values: Any) -> str:
    return json.dumps(values, sort_keys=True, allow_nan=False)
