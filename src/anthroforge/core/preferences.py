"""Application execution choices, independent of authored project state."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Preferences:
    routing_backend: str = "CUSTOM"
    routing_conversion_points: str = "ENDPOINTS"
    fiber_propagation: str = "SMOOTH_SHAPE"
    autosave_enabled: bool = True
    autosave_minutes: int = 5
    skin_tissue_surface: str = "FINISHED"

    def __post_init__(self) -> None:
        if self.routing_backend not in ("CUSTOM", "PIQP"):
            raise ValueError("ROUTED solver must be CUSTOM or PIQP.")
        if self.routing_conversion_points not in ("ENDPOINTS", "ALL_POINTS"):
            raise ValueError("ROUTED conversion points must be ENDPOINTS or ALL_POINTS.")
        if self.fiber_propagation not in ("SMOOTH_SHAPE", "LOCAL_SURFACE"):
            raise ValueError("Fiber propagation must be SMOOTH_SHAPE or LOCAL_SURFACE.")
        if type(self.autosave_enabled) is not bool:
            raise ValueError("Autosave enabled must be true or false.")
        if type(self.autosave_minutes) is not int or not 1 <= self.autosave_minutes <= 1440:
            raise ValueError("Autosave interval must be a whole number from 1 to 1440 minutes.")
        if self.skin_tissue_surface not in ("FINISHED", "INFLATED_REST"):
            raise ValueError("Skin tissue surface must be FINISHED or INFLATED_REST.")
