"""Application execution choices, independent of authored project state."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Preferences:
    routing_backend: str = "CUSTOM"
    routing_conversion_points: str = "ENDPOINTS"

    def __post_init__(self) -> None:
        if self.routing_backend not in ("CUSTOM", "PIQP"):
            raise ValueError("ROUTED solver must be CUSTOM or PIQP.")
        if self.routing_conversion_points not in ("ENDPOINTS", "ALL_POINTS"):
            raise ValueError("ROUTED conversion points must be ENDPOINTS or ALL_POINTS.")
