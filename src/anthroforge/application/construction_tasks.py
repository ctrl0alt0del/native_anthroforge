"""Construction job admission and complete, revision-checked result publication."""

from functools import partial
from typing import TYPE_CHECKING, Any, cast
from uuid import uuid4

from anthroforge.core.document import Document
from anthroforge.core.jobs import Job
from anthroforge.core.primitive_sampling import counts
from anthroforge.core.scheduling import Workload
from anthroforge.core.surfaces import Surface
from anthroforge.native.mesh import NativeCancellation

from . import dependencies as dep
from . import geometry_outputs, surface_evaluation
from .assets import Asset
from .construction_evaluator import Evaluation
from .construction_policy import mode, revisions
from .construction_scheduling import stages
from .curve_sources import source as source_curve
from .evaluation_results import accepted_result as accepted_result

if TYPE_CHECKING:
    from .session import Session


def request(session: "Session", entity: str, interactive: bool = False) -> str:
    from .path_tasks import prerequisites

    prerequisites(session, entity)
    job = make_job(session, entity)
    job.cancel = NativeCancellation(session.engine)
    job.interactive, job.priority = interactive, session.priority({entity})
    job.publish_during_edit = job.restart_on_redo = True
    job.retry = partial(request, session, entity)
    job.workload = partial(workload, session, entity)
    job.cleanup = partial(completed, session, entity, job)
    dep.renewable_contract(job, session.document, {dep.Port(entity, "geometry")})
    return session.scheduler.submit(job)


def make_job(session: "Session", entity: str) -> Job:
    job = Job(
        "Evaluate " + session.document.object(entity).name,
        frozenset((entity,)),
        lambda document: (document, session.resources.snapshot()),
        partial(compute, session, entity),
        partial(publish, session, entity),
        key="construction:" + entity,
        kind="construction",
        reads=frozenset(dep.reads(session.document, entity)),
    )
    return job


def workload(session: "Session", entity: str, document: Document) -> Workload:
    item = document.object(entity)
    if isinstance(item, Surface):
        return surface_workload(session, item, document)
    return primitive_workload(session, entity, document)


def primitive_workload(session: "Session", entity: str, document: Document) -> Workload:
    item = document.entity(entity)
    primitive = item.primitive
    points = (
        sum(len(source_curve(document, c.id).points) for c in primitive.curves) if primitive else 0
    )
    vertices = sum(counts(primitive).values()) if primitive else 0
    return Workload(
        entities=len(document.entities),
        affected=1,
        candidates=points,
        triangles=vertices * (primitive.strips if primitive else 1) * 2,
        stages=stages(session, document, entity),
    )


def compute(session: "Session", entity: str, payload: Any, cancel: Any) -> Any:
    document, resources = payload
    if dep.Port(entity, "geometry") in dep.blocked(dep.graph(document)):
        raise ValueError(
            "Cyclic or missing construction dependency; last accepted geometry retained."
        )
    return document, compute_geometry(session, document, resources, entity, cancel)


def compute_geometry(
    session: "Session", document: Document, resources: Any, entity: str, cancel: Any
) -> Any:
    item = document.object(entity)
    if isinstance(item, Surface):
        return surface_evaluation.evaluate(session.engine, document, resources, item, cancel.handle)
    meshes = {key: asset.mesh for key, asset in resources.meshes.items()}
    evaluator = Evaluation(
        session.engine, document, meshes, cast(NativeCancellation, cancel), resources.paths
    )
    return evaluator.geometry(document.entity(entity))


def publish(session: "Session", entity: str, result: Any) -> None:
    source, mesh = result
    inputs = dep.ports(source, dep.Port(entity, "geometry"))
    if revisions(source, inputs) != revisions(session.document, inputs):
        raise ValueError("Construction inputs changed before publication.")
    item = geometry_outputs.get(session.document, entity)
    key = str(uuid4())
    session.assets[key] = Asset(mesh, "generated", "", 1.0, False)
    accepted = accepted_result(source, item, inputs, key)
    geometry_outputs.install(session, item, accepted)
    propagate_result(session, entity)


def completed(session: "Session", entity: str, job: Job, state: str) -> None:
    if state == "failed":
        geometry_outputs.failed(session, entity, job.error)


def propagate_result(session: "Session", entity: str) -> None:
    from anthroforge.core.entities import descendants

    from . import evaluation
    from .dependent_tasks import changed

    changed(session, {dep.Port(entity, "geometry")})
    targets = descendants(session.document.entities, entity) - {entity}
    live = {key for key in targets if mode(session.document, key) != "MANUAL"}
    if live and session.document.attachments_enabled:
        evaluation.request(session, live)


def schedule(
    session: "Session", targets: set[str], released: bool = False, explicit: bool = False
) -> list[str]:
    scheduled = []
    for entity in geometry_outputs.items(session.document):
        if entity.id in targets:
            setting = mode(session.document, entity.id)
            if explicit or setting == "LIVE" or (released and setting == "ON_RELEASE"):
                scheduled.append(request(session, entity.id, interactive=not released))
    return scheduled


def edited(session: "Session", targets: set[str]) -> None:
    from .dependent_tasks import changed

    if not targets:
        return
    changed(session, {dep.Port(key, "geometry") for key in targets}, published=False)


def evaluate(session: "Session", entities: list[str] | None = None) -> list[str]:
    from .path_tasks import prerequisites

    eligible = {e.id for e in geometry_outputs.items(session.document)}
    targets = set(entities) & eligible if entities is not None else eligible
    for entity in tuple(targets):
        prerequisites(session, entity, explicit=True)
        targets.update(dep.reads(session.document, entity) & eligible)
    return schedule(session, targets, explicit=True)


def surface_workload(session: "Session", item: Surface, document: Document) -> Workload:
    from anthroforge.core.scheduling import StageWorkload

    paths = session.resources.paths
    sources = [source_curve(document, use.curve).result.asset for use in item.curves]
    points = sum(paths[key].path.count for key in sources if key in paths)
    rows = len(item.curves) + sum(item.across)
    polygons = points * rows if item.kind == "LOFT" else points * item.patch_resolution**2
    return Workload(
        affected=1,
        candidates=points,
        triangles=polygons * 2,
        stages=(StageWorkload("surface", points, polygons),),
    )
