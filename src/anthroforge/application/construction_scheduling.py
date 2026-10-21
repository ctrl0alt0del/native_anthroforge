"""Stage-specific estimates compose into one coordinated geometry job.

Initial coefficients are conservative heuristics in milliseconds, not latency guarantees.
Measured complete-job costs in ConstructionTaskScheduler can only increase the estimate.
"""

from typing import Any, Protocol

from anthroforge.core.primitive_sampling import counts
from anthroforge.core.scheduling import StageWorkload


class StagePolicy(Protocol):
    def estimate(self, workload: StageWorkload) -> float: ...


class PrimitiveStagePolicy:
    def estimate(self, workload: StageWorkload) -> float:
        return 0.1 + workload.points * 0.002 + workload.polygons * 0.004


class HookStagePolicy:
    def estimate(self, workload: StageWorkload) -> float:
        return 0.02 + workload.points * 0.0003


class LatticeStagePolicy:
    def estimate(self, workload: StageWorkload) -> float:
        return 0.05 + workload.points * 0.008


class ThicknessStagePolicy:
    def estimate(self, workload: StageWorkload) -> float:
        return 0.1 + workload.points * 0.002 + workload.polygons * 0.003


class ShrinkwrapStagePolicy:
    def estimate(self, workload: StageWorkload) -> float:
        return 0.1 + workload.points * 0.01


class UnionStagePolicy:
    def estimate(self, workload: StageWorkload) -> float:
        return 5.0 + workload.polygons * 0.05


class SurfaceStagePolicy:
    def estimate(self, workload: StageWorkload) -> float:
        return 0.2 + workload.points * 0.003 + workload.polygons * 0.004


POLICIES: dict[str, StagePolicy] = {
    "construction": PrimitiveStagePolicy(),
    "HOOK": HookStagePolicy(),
    "LATTICE": LatticeStagePolicy(),
    "thickness": ThicknessStagePolicy(),
    "surface": SurfaceStagePolicy(),
    "SHRINKWRAP": ShrinkwrapStagePolicy(),
    "UNION": UnionStagePolicy(),
}


def estimate(stages: tuple[StageWorkload, ...]) -> float:
    return sum(POLICIES[stage.kind].estimate(stage) for stage in stages)


def parametric_size(primitive: Any) -> tuple[int, int]:
    if primitive.kind == "BODY":
        density = counts(primitive)
        points = sum(
            density[p.curve] * (4 if p.shape == "BOX" else p.sides) for p in primitive.pieces
        )
        return points, points + 2 * len(primitive.pieces)
    strips = (len(primitive.curves) - 1) * primitive.strips
    samples = max(counts(primitive).values())
    return samples * (strips + 1), samples * strips + 2 * int(primitive.caps)


def mesh_size(session: Any, item: Any) -> tuple[int, int]:
    primitive = item.primitive
    if primitive.chain:
        points = sum(s.samples * s.sides for s in primitive.chain.segments)
        return points, points + 2 * len(primitive.chain.segments)
    if primitive.kind == "IMPORTED":
        dimensions = session.assets[primitive.source].mesh.counts
        return dimensions[0], dimensions[1]
    return parametric_size(primitive)


def stages(session: Any, document: Any, entity: str) -> tuple[StageWorkload, ...]:
    item = document.entity(entity)
    points, faces = mesh_size(session, item)
    result = [StageWorkload("construction", points, faces)]
    if item.primitive.chain and item.primitive.chain.unite:
        result.append(StageWorkload("UNION", points, faces))
    for binding in item.deformers:
        result.extend(binding_stages(document, item, binding, points))
    if item.thickness and item.thickness.enabled:
        result.append(StageWorkload("thickness", points, faces))
    return tuple(result)


def binding_stages(document: Any, item: Any, binding: Any, points: int) -> list[StageWorkload]:
    if not binding.enabled:
        return []
    if binding.target.stage == "CURVE":
        points = 3 * len(document.object(binding.target.component).points)
    result = [StageWorkload(binding.kind, points)]
    if not binding.control:
        return result
    control = document.control(binding.control)
    result.extend(
        StageWorkload(b.kind, len(control.points)) for b in control.deformers if b.enabled
    )
    return result
