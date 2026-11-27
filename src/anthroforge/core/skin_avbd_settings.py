"""AVBD configuration and source routing are independent of FIELD controls."""

import json
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from .skin_draft import BuilderConfiguration
from .skin_limb import SkinLimb
from .skin_validation import choice


@dataclass(frozen=True, slots=True)
class AvbdContributor:
    owner: str
    build_mode: str = "INHERIT"
    limb: SkinLimb | None = None

    def __post_init__(self) -> None:
        if not self.owner:
            raise ValueError("AVBD contributor requires a source identity.")
        choice("skin building mode", self.build_mode, ("INHERIT", "FOLLOW", "FILL"))
        if self.limb is not None and not isinstance(self.limb, SkinLimb):
            raise ValueError("Invalid limb settings.")


@dataclass(frozen=True, slots=True)
class AvbdConfiguration:
    plan: str = "{}"
    contributors: tuple[AvbdContributor, ...] = ()

    def __post_init__(self) -> None:
        value = json.loads(self.plan)
        if not isinstance(value, dict) or value.keys() - {"bones", "muscles", "normalization"}:
            raise ValueError("AVBD plan accepts bones, muscles and normalization.")
        for key in ("bones", "muscles"):
            if key in value:
                validate_rows(key, value[key])
        if len({r.owner for r in self.contributors}) != len(self.contributors):
            raise ValueError("Duplicate AVBD contributor settings.")
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


def contributor(values: dict[str, Any]) -> AvbdContributor:
    values = dict(values)
    if values.get("limb") is not None:
        values["limb"] = SkinLimb(**values["limb"])
    return AvbdContributor(**values)


@lru_cache(maxsize=256)
def decode(record: BuilderConfiguration) -> AvbdConfiguration:
    values = record.values()
    rows = tuple(contributor(row) for row in values.pop("contributors", ()))
    if record.builder != "AVBD":
        raise ValueError("Unsupported AVBD configuration.")
    return AvbdConfiguration(contributors=rows, **values)


def settings_for(skin: Any, owner: str) -> AvbdContributor:
    rows = decode(skin.draft_settings.configuration("AVBD")).contributors
    return next((row for row in rows if row.owner == owner), AvbdContributor(owner))
