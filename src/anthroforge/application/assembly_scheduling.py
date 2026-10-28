"""Import policies estimate package IO and selected graph work without another executor."""

from typing import Any

from anthroforge.core.scheduling import ResourceDemand, Schedule

from .task_schedulers import MeasuredTaskScheduler


class AssemblyTaskScheduler(MeasuredTaskScheduler):
    def plan(self, workload: Any, interactive: bool) -> Schedule:
        cost = 1 + workload.bytes / 100_000 + workload.candidates * 0.05
        return Schedule(
            "worker",
            cost,
            reason="Pinned project graph preparation",
            resources=ResourceDemand(1, workload.bytes),
        )


def policies() -> dict[str, Any]:
    names = ("assembly_inspect", "assembly_prepare", "skeleton_prepare")
    return {name: AssemblyTaskScheduler() for name in names}
