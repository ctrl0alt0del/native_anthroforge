"""Per-task admission policies. Only the coordinator owns queues and execution."""

from collections import defaultdict, deque
from dataclasses import replace
from typing import Literal, Protocol

from anthroforge.core.document import Document
from anthroforge.core.jobs import Job
from anthroforge.core.scheduling import Assessment, Schedule, Workload

INLINE_BUDGET_MS = 2.0
INLINE_WINDOW_MS = 16.0
MAX_INTERACTIVE_WAIT_MS = 100.0


class TaskScheduler(Protocol):
    def assess(self, job: Job, document: Document) -> Assessment: ...

    def observe(self, job: Job) -> None: ...


class MeasuredTaskScheduler:
    def __init__(self) -> None:
        self.samples: dict[tuple[int, ...], deque[float]] = defaultdict(lambda: deque(maxlen=32))

    def assess(self, job: Job, document: Document) -> Assessment:
        workload = job.workload(document)
        plan = self.plan(workload, job.interactive)
        samples = self.samples.get(workload.bucket(), ())
        estimate = (
            max(plan.estimated_ms or 0.0, max(samples) * 1.25) if samples else plan.estimated_ms
        )
        plan = replace(plan, estimated_ms=estimate)
        return Assessment(workload, self.adjust(plan, job.interactive))

    def observe(self, job: Job) -> None:
        if job.assessment is not None and job.state == "succeeded":
            cost = job.prepare_ms + job.compute_ms + job.publish_ms
            self.samples[job.assessment.workload.bucket()].append(cost)

    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        return Schedule()

    def adjust(self, plan: Schedule, interactive: bool) -> Schedule:
        return plan


class AttachmentTaskScheduler(MeasuredTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        cost = attachment_cost(workload)
        bounded = (
            workload.entities <= 64 and workload.candidates <= 64 and workload.triangles <= 256
        )
        mode: Literal["inline", "worker"] = "worker"
        if interactive and bounded and cost <= INLINE_BUDGET_MS and not workload.recaptures:
            mode = "inline"
        reason = (
            "Bounded native attachment update" if mode == "inline" else "Background attachments"
        )
        return Schedule(mode, cost, reason=reason)

    def adjust(self, plan: Schedule, interactive: bool) -> Schedule:
        estimate = plan.estimated_ms or 0.0
        if plan.execution == "inline" and estimate > INLINE_BUDGET_MS:
            plan = replace(plan, execution="worker", reason="Measured cost exceeds inline budget")
        if interactive and plan.execution == "worker":
            delay = min(MAX_INTERACTIVE_WAIT_MS, max(INLINE_WINDOW_MS, estimate * 2))
            return replace(plan, delay_ms=delay, max_wait_ms=MAX_INTERACTIVE_WAIT_MS)
        return plan


def attachment_cost(workload: Workload) -> float:
    # Includes current full-document ordering/packing, not only affected objects.
    return (
        0.1
        + 0.006 * workload.entities
        + 0.0002 * workload.entities**2
        + 0.01 * workload.affected
        + 0.002 * workload.candidates
        + 0.001 * workload.triangles
    )


class ImportTaskScheduler(MeasuredTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        return Schedule(reason="Explicit mesh import; parsing and BVH construction stay background")


class ImageTaskScheduler(MeasuredTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        return Schedule(reason="Image decode and texture tile preparation stay background")


class CurveDrawingTaskScheduler(MeasuredTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        cost = 0.2 + workload.candidates * 0.02
        return Schedule("worker", cost, reason="Native stroke fitting and path preparation")


class SurfaceLayoutTaskScheduler(MeasuredTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        cost = 0.2 + workload.candidates**2 * 0.001 + workload.triangles * 0.004
        return Schedule(
            "worker", cost, reason="Explicit native surface correspondence and construction"
        )


class OpenProjectTaskScheduler(MeasuredTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        return Schedule(reason="Explicit project open; decompression stays background")


class SaveProjectTaskScheduler(MeasuredTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        return Schedule(reason="Explicit project save; compression and disk writes stay background")


class ConstructionTaskScheduler(MeasuredTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        from .construction_scheduling import estimate

        cost = estimate(workload.stages)
        return Schedule(
            "worker",
            cost,
            max_wait_ms=MAX_INTERACTIVE_WAIT_MS,
            reason="Native stage pipeline, normals, buffers and spatial indexing",
        )

    def adjust(self, plan: Schedule, interactive: bool) -> Schedule:
        cost = plan.estimated_ms or 0
        delay = min(MAX_INTERACTIVE_WAIT_MS, max(INLINE_WINDOW_MS, cost)) if interactive else 0
        return replace(plan, delay_ms=delay)


class ControlPoseTaskScheduler(AttachmentTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        cost = 0.1 + 0.01 * workload.candidates
        execution: Literal["inline", "worker"] = (
            "inline" if interactive and workload.candidates <= 32 else "worker"
        )
        return Schedule(execution, cost, reason="Ordinary control transform resolution")


class CurvePathTaskScheduler(AttachmentTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        # Conservative initial heuristic; observed preparation/compute/publication raises it.
        cost = 0.1 + workload.candidates * 0.01 + workload.triangles * 0.003
        bounded = workload.candidates <= 32 and workload.triangles <= 256
        execution: Literal["inline", "worker"] = (
            "inline" if interactive and bounded and cost < INLINE_BUDGET_MS else "worker"
        )
        return Schedule(execution, cost, reason="Owned native path evaluation")


class IssueTaskScheduler(MeasuredTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        cost = 0.1 + 0.005 * workload.affected
        delay = 0.0 if workload.affected < 64 else min(150.0, max(25.0, cost * 2))
        return Schedule("worker", cost, delay, 150.0, "Read-only advisory checks after editing")


class FiberCaptureTaskScheduler(MeasuredTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        cost = 0.2 + workload.candidates * max(1, workload.entities) * 0.02
        return Schedule("worker", cost, reason="Dense anatomical capture and owner blending")


class SurfaceQueryTaskScheduler(MeasuredTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        cost = 0.5 + workload.triangles * 0.2 + workload.candidates * 0.01
        return Schedule("worker", cost, reason="Exterior query preparation and confirmed placement")


class FiberPathTaskScheduler(AttachmentTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        cost = 0.1 + workload.candidates * 0.02 + workload.triangles * 0.002
        return Schedule("worker", cost, reason="Dense fiber resolution or edit and recapture")


class AttachedConstructionTaskScheduler(MeasuredTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        capture = FiberCaptureTaskScheduler().plan(workload, interactive)
        surface = SurfaceLayoutTaskScheduler().plan(workload, interactive)
        cost = (capture.estimated_ms or 0) + (surface.estimated_ms or 0)
        return Schedule(
            "worker", cost, reason="Atomic attachment capture and membrane construction"
        )


class RoutingTaskScheduler(AttachmentTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        cost = 1.0 + workload.candidates * 0.1 + workload.triangles * 0.01
        return Schedule("worker", cost, reason="Native obstacle routing and constrained solve")


class InspectionTaskScheduler(SaveProjectTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        return Schedule(reason="Frozen inspection export; file and GPU work stay background")


class TissueInspectionTaskScheduler(MeasuredTaskScheduler):
    def plan(self, workload: Workload, interactive: bool) -> Schedule:
        cost = 0.2 + workload.triangles * 0.004
        return Schedule(
            "worker", cost, reason="Read-only material comparison and constraint inspection"
        )


def task_schedulers() -> dict[str, TaskScheduler]:
    return {
        "generic": MeasuredTaskScheduler(),
        "attachments": AttachmentTaskScheduler(),
        "mesh_import": ImportTaskScheduler(),
        "image_decode": ImageTaskScheduler(),
        "project_open": OpenProjectTaskScheduler(),
        "project_save": SaveProjectTaskScheduler(),
        "construction": ConstructionTaskScheduler(),
        **curve_schedulers(),
        **anchor_schedulers(),
        "control_pose": ControlPoseTaskScheduler(),
        **inspection_schedulers(),
    }


def inspection_schedulers() -> dict[str, TaskScheduler]:
    return dict(
        issue_check=IssueTaskScheduler(),
        inspection_report=InspectionTaskScheduler(),
        tissue_inspection=TissueInspectionTaskScheduler(),
    )


def curve_schedulers() -> dict[str, TaskScheduler]:
    return {
        "curve_path": CurvePathTaskScheduler(),
        "curve_routing": RoutingTaskScheduler(),
        "curve_draw": CurveDrawingTaskScheduler(),
        "surface_layout": SurfaceLayoutTaskScheduler(),
        "fiber_capture": FiberCaptureTaskScheduler(),
        "surface_snap": SurfaceQueryTaskScheduler(),
        "fiber_path": FiberPathTaskScheduler(),
    }


def anchor_schedulers() -> dict[str, TaskScheduler]:
    from .tissue_scheduling import policies

    return {
        "anchor_capture": FiberCaptureTaskScheduler(),
        "attached_construction": AttachedConstructionTaskScheduler(),
        "anchor_binding": AttachmentTaskScheduler(),
        **policies(),
    }
