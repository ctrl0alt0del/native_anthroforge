"""Named native quality observations; unavailable checks are never successful checks."""

from dataclasses import dataclass

QUALITY = (
    "finite",
    "components",
    "watertight",
    "orientable",
    "positive_volume",
    "no_degenerates",
    "minimum_triangle_area2",
    "volume",
    "edges",
)
COVERAGE = (
    "source_vertices_outside",
    "source_triangles_crossed",
    "source_vertices_checked",
    "source_triangles_checked",
    "protected_gap_checks",
    "protected_gap_violations",
    "minimum_gap_clearance",
)


@dataclass(frozen=True, slots=True)
class Diagnostics:
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.values) != 19 or self.values[0] not in range(8):
            raise ValueError("Invalid native skin diagnostic record.")

    @property
    def unavailable(self) -> tuple[str, ...]:
        groups = ((1, "mesh_quality"), (2, "coverage"), (4, "source_intersections"))
        return tuple(name for bit, name in groups if not int(self.values[0]) & bit)

    def report(self) -> dict[str, object]:
        mask = int(self.values[0])
        return dict(
            mesh_quality=dict(zip(QUALITY, self.values[1:10], strict=True)) if mask & 1 else None,
            coverage=dict(zip(COVERAGE, self.values[10:17], strict=True)) if mask & 2 else None,
            source_intersections=self.values[17] if mask & 4 else None,
            unsupported_components_removed=self.values[18],
            unavailable=self.unavailable,
        )
