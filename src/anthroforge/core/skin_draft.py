"""Authored selection of the algorithm that builds the project's draft surface."""

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DraftSettings:
    backend: str = "FIELD"
    plan: str = "{}"

    def __post_init__(self) -> None:
        if not isinstance(self.backend, str) or not self.backend.strip():
            raise ValueError("A draft builder needs an identifier.")
        value = json.loads(self.plan)
        if not isinstance(value, dict) or value.keys() - {"bones", "muscles", "normalization"}:
            raise ValueError("AVBD plan accepts bones, muscles and normalization.")
        for key in ("bones", "muscles"):
            if key in value:
                validate_rows(key, value[key])
        object.__setattr__(self, "plan", json.dumps(value, sort_keys=True, allow_nan=False))


def validate_rows(key: str, rows: Any) -> None:
    if not isinstance(rows, list):
        raise ValueError(f"AVBD {key} must be an ordered list.")
    fields = {"id", "route", "settings", "joint"} if key == "bones" else {"id", "frames"}
    ids = set()
    for row in rows:
        if not isinstance(row, dict) or row.keys() - fields or not isinstance(row.get("id"), str):
            raise ValueError(f"Invalid AVBD {key} stage. Allowed fields: {sorted(fields)}")
        if not row["id"] or row["id"] in ids:
            raise ValueError(f"Empty or duplicate AVBD {key} identity: {row['id']}")
        ids.add(row["id"])
