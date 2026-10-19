"""Authored stacking intent and accepted geometric order are distinct records."""

from dataclasses import dataclass

from .tissue_settings import finite_range


@dataclass(frozen=True, slots=True)
class StackSettings:
    search: float = 0.05
    clearance: float = 0.0
    radius: float = 0.5
    strength: float = 0.8
    blend: float = 1.0
    preservation: float = 100.0
    adjustment: float = 4.0

    def __post_init__(self) -> None:
        for name in ("search", "clearance", "radius", "strength", "blend", "adjustment"):
            finite_range(getattr(self, name), 0, 1000, "Stacking " + name)
        finite_range(self.preservation, 1, 1000000, "Stacking preservation")


@dataclass(frozen=True, slots=True)
class StackRelationship:
    other: str
    side: str = "a"
    other_side: str = "a"
    mode: str = "AUTO"
    cover: str = "SELF"
    excluded: bool = False
    regions: tuple[tuple[str, int], ...] = ()
    topology: str = ""

    def __post_init__(self) -> None:
        if not self.other or self.side not in ("a", "b") or self.other_side not in ("a", "b"):
            raise ValueError("Choose two tissue sides for the stacking relationship.")
        if self.mode not in ("AUTO", "REQUESTED", "EXPLICIT") or self.cover not in (
            "SELF",
            "OTHER",
        ):
            raise ValueError("Choose automatic, requested or explicit stacking order.")
        if self.regions and (self.mode == "AUTO" or not self.topology):
            raise ValueError(
                "Selected support regions require an explicit covering side and topology."
            )
        if any(not part or face < 0 for part, face in self.regions):
            raise ValueError("Support regions require valid part and material face identities.")


@dataclass(frozen=True, slots=True)
class StackOrder:
    first: str
    second: str
    side: str
    other_side: str
    underlying: str = ""
    covering: str = ""
    status: int = 0
    diagnostic: str = ""
    fragments: int = 0


@dataclass(frozen=True, slots=True)
class StackPlan:
    providers: tuple[str, ...] = ()
    orders: tuple[StackOrder, ...] = ()
    error: str = ""
