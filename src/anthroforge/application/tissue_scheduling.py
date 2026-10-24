"""Stage-specific cost policies; the existing coordinator owns dispatch and workers."""

from anthroforge.core.scheduling import Schedule, Workload

from .task_schedulers import ConstructionTaskScheduler


class TissueTaskScheduler(ConstructionTaskScheduler):
    def __init__(self, phase: str, cost_per_vertex: float) -> None:
        super().__init__()
        self.phase, self.cost_per_vertex = phase, cost_per_vertex

    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        cost = 0.2 + workload.candidates * self.cost_per_vertex
        return Schedule("worker", cost, reason="Native tissue " + self.phase)


def policies() -> dict[str, TissueTaskScheduler]:
    costs = dict(
        base=0.001,
        rest=0.008,
        intrinsic=0.02,
        plan=0.01,
        final=0.03,
        constraint_capture=0.02,
        source_replace=0.069,
    )
    return {"tissue_" + phase: TissueTaskScheduler(phase, cost) for phase, cost in costs.items()}
