"""Cheap planning metadata is separate from the owned inputs captured at execution."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class RequestUrgency:
    interactive: bool
    since: float


@dataclass(frozen=True)
class QueueDemand:
    priority: int
    since: float
    queued: float
    source: str

    @property
    def key(self) -> tuple[int, float, float]:
        return -self.priority, self.since, self.queued


@dataclass(frozen=True)
class StageWorkload:
    kind: str
    points: int = 0
    polygons: int = 0


@dataclass(frozen=True)
class Workload:
    entities: int = 0
    affected: int = 0
    recaptures: int = 0
    candidates: int = 0
    triangles: int = 0
    bytes: int = 0
    stages: tuple[StageWorkload, ...] = ()

    def bucket(self) -> tuple[int, ...]:
        values: tuple[int, ...] = (
            self.entities,
            self.affected,
            self.recaptures,
            self.candidates,
            self.triangles,
            self.bytes,
        )
        values += tuple(stage.points + stage.polygons for stage in self.stages)
        return tuple(value.bit_length() for value in values)


@dataclass(frozen=True)
class Schedule:
    execution: Literal["inline", "worker"] = "worker"
    estimated_ms: float | None = None
    delay_ms: float = 0.0
    max_wait_ms: float = 0.0
    reason: str = "Background work"


@dataclass(frozen=True)
class Assessment:
    workload: Workload
    schedule: Schedule
