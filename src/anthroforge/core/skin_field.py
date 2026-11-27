"""FIELD envelope parameters and per-source overrides; no AVBD dependencies."""

from dataclasses import dataclass, field, replace
from functools import lru_cache
from typing import Any

from .skin_draft import BuilderConfiguration
from .skin_validation import bounded, choice


@dataclass(frozen=True, slots=True)
class EnvelopeSettings:
    minimum_offset_ratio: float = 1.189424086064195 / 220.0
    collagen_depth_ratio: float = (3.1717975628378534 - 1.189424086064195) / 220.0
    collagen_core_ratio: float = 4.75769634425678 / 220.0
    collagen_falloff_ratio: float = (13.480139642060877 - 4.75769634425678) / 220.0
    gap_limit_ratio: float = 0.005
    gap_strength: float = 1.0

    def __post_init__(self) -> None:
        limits = (0.02, 0.04, 0.05, 0.10, 1.0, 1.0)
        for name, limit in zip(self.__dataclass_fields__, limits, strict=True):
            bounded(name, getattr(self, name), 0, limit)


@dataclass(frozen=True, slots=True)
class FieldContributor:
    owner: str
    collagen_mode: str = "AUTO"
    collagen: float = 1.0
    painted: str = ""
    gap_mode: str = "INHERIT"
    gap_limit_ratio: float = 0.005
    gap_strength: float = 1.0

    def __post_init__(self) -> None:
        if not self.owner:
            raise ValueError("FIELD contributor requires a source identity.")
        choice("collagen mode", self.collagen_mode, ("AUTO", "UNIFORM", "PAINTED"))
        choice("gap mode", self.gap_mode, ("INHERIT", "OVERRIDE"))
        bounded("collagen", self.collagen, 0, 1)
        bounded("gap limit", self.gap_limit_ratio, 0, 1)
        bounded("gap strength", self.gap_strength, 0, 1)


@dataclass(frozen=True, slots=True)
class FieldConfiguration:
    settings: EnvelopeSettings = field(default_factory=EnvelopeSettings)
    contributors: tuple[FieldContributor, ...] = ()

    def __post_init__(self) -> None:
        if len({r.owner for r in self.contributors}) != len(self.contributors):
            raise ValueError("Duplicate FIELD contributor settings.")


@lru_cache(maxsize=256)
def decode(record: BuilderConfiguration) -> FieldConfiguration:
    values = record.values()
    rows = tuple(FieldContributor(**r) for r in values.pop("contributors", ()))
    settings = EnvelopeSettings(**values.pop("settings", {}))
    if values or record.builder != "FIELD":
        raise ValueError("Unsupported FIELD configuration.")
    return FieldConfiguration(settings, rows)


def effective_collagen(settings: FieldContributor, name: str) -> float:
    if settings.collagen_mode != "AUTO":
        return settings.collagen
    return 0.0 if any(term in name.lower() for term in ("ear", "cartilage", "nasal")) else 1.0


def effective(config: FieldConfiguration, row: FieldContributor, name: str) -> FieldContributor:
    gap = row if row.gap_mode == "OVERRIDE" else config.settings
    return replace(
        row,
        collagen=effective_collagen(row, name),
        gap_limit_ratio=gap.gap_limit_ratio,
        gap_strength=gap.gap_strength,
    )


def settings_for(skin: Any, owner: str) -> FieldContributor:
    rows = decode(skin.draft_settings.configuration("FIELD")).contributors
    return next((row for row in rows if row.owner == owner), FieldContributor(owner))
