"""Native expression declarations use canonical quantities and explicit numerical types."""

from dataclasses import dataclass

DIMENSIONS = {"SCALAR": (0, 0), "LENGTH": (1, 0), "ANGLE": (0, 1)}
KINDS = {"INTEGER": 0, "REAL": 1}
RESERVED = frozenset(
    "pi e m rad sin cos tan asin acos atan atan2 sqrt abs exp log log10 "
    "floor ceil round min max clamp pow".split()
)


@dataclass(frozen=True, slots=True)
class Symbol:
    name: str
    numeric_type: str = "REAL"
    dimension: str = "SCALAR"

    def __post_init__(self) -> None:
        if not self.name.isascii() or not self.name.isidentifier() or self.name.startswith("_"):
            raise ValueError("Expression inputs require public ASCII identifiers.")
        if self.name in RESERVED:
            raise ValueError("Expression input name is reserved.")
        if self.numeric_type not in KINDS or self.dimension not in DIMENSIONS:
            raise ValueError("Invalid expression input type or physical quantity.")

    @property
    def native_type(self) -> tuple[int, int, int]:
        return (KINDS[self.numeric_type], *DIMENSIONS[self.dimension])


@dataclass(frozen=True, slots=True)
class ResultType:
    kind: int
    length: int
    angle: int
    zero: bool

    def require(self, kind: str, dimension: str) -> None:
        if self.kind == 1 and kind == "INTEGER":
            raise ValueError("Integer targets require integer results; use round, floor or ceil.")
        if not self.zero and (self.length, self.angle) != DIMENSIONS[dimension]:
            raise ValueError(f"Expression dimensions do not match target quantity {dimension}.")
