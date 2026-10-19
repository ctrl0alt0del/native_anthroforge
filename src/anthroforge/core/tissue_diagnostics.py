"""Accepted stage diagnostics are distinct from authored strategies and failure state."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TissueDiagnostic:
    stage: str = "intrinsic"
    status: str = "NOT_APPLICABLE"
    iterations: int = 0
    final_change: float = 0.0
    max_displacement: float = 0.0
    relative_volume_error: float = 0.0
    max_fixed_error: float = 0.0
    solve_ms: float = 0.0
    part: str = ""
    side: str = ""
    samples: int = 0
    pinned: int = 0
    skipped_triangles: int = 0
    total_ms: float = 0.0
    violation: float = 0.0
    stationarity: float = 0.0
    complementarity: float = 0.0
    complementarity_relative: float = 0.0
    objective: float = 0.0
