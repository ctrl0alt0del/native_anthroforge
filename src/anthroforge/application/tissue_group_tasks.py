"""A coupled final bundle uses the existing coordinator and one atomic publication."""

from dataclasses import replace
from functools import partial
from typing import Any

from anthroforge.core import tissue_groups
from anthroforge.core.jobs import Job, ObsoleteInputs
from anthroforge.core.results import Port
from anthroforge.core.scheduling import Workload
from anthroforge.native.mesh import NativeCancellation

from . import dependencies as dep
from . import tissue_group_evaluation, tissue_results, tissue_stack_observation
from .construction_policy import mode, revisions


def grouped(document: Any, target: str) -> bool:
    return len(tissue_groups.members(document.registry.authored, target)) > 1


def targets_for(session: Any, target: str) -> tuple[frozenset[str], str]:
    group = tissue_groups.members(session.document.registry.authored, target)
    selected = {key for key in group if key == target or mode(session.document, key) == "LIVE"}
    return frozenset(selected), "tissue:group:" + ":".join(sorted(group))


def request(session: Any, target: str, interactive: bool) -> str:
    targets, key = targets_for(session, target)
    active = next((j for j in session.scheduler.active_jobs if j.key == key), None)
    if active and targets.issubset(active.outputs):
        return str(active.id)
    targets |= active.outputs if active else frozenset()
    job = make_job(session, targets, key)
    job.interactive, job.priority = interactive, session.priority(set(targets))
    job.retry = partial(request, session, target, interactive)
    return str(session.scheduler.submit(job))


def make_job(session: Any, targets: Any, key: str) -> Job:
    job = Job(
        "Stack tissue group",
        targets,
        lambda doc: (doc, session.resources.snapshot()),
        partial(compute, session, targets),
        partial(publish, session, targets),
        key=key,
        kind="tissue_final",
        reads=targets,
    )
    configure_job(session, targets, job)
    return job


def configure_job(session: Any, targets: Any, job: Job) -> None:
    job.cancel = NativeCancellation(session.engine)
    job.publish_during_edit = job.restart_on_redo = job.restart_on_input_change = True
    job.cleanup = partial(completed, session, targets, job)
    job.workload = partial(workload, session, targets)
    dep.contract(job, session.document, {Port(key, "final") for key in targets})
    job.observes |= frozenset(observed(session.document, targets))
    job.reads |= frozenset(p.owner for p in job.observes)


def workload(session: Any, targets: Any, document: Any) -> Workload:
    from .tissue_tasks import workload as single

    values = [single(session, key, "final", document) for key in targets]
    return Workload(
        affected=len(targets),
        candidates=sum(v.candidates for v in values),
        triangles=sum(v.triangles for v in values),
        entities=sum(v.entities for v in values),
    )


def observed(document: Any, targets: Any) -> set[Port]:
    return set().union(
        *(
            dep.ports(document, Port(key, "final"))
            | tissue_stack_observation.ports(document, key, "final")
            for key in targets
        )
    )


def compute(session: Any, targets: Any, payload: Any, cancel: Any) -> Any:
    document, resources = payload
    if any(Port(key, "final") in dep.blocked(dep.graph(document)) for key in targets):
        raise ValueError("Cyclic or missing tissue dependency; accepted geometry retained.")
    values = tissue_group_evaluation.evaluate(
        session.engine, document, resources, targets, cancel.handle
    )
    return document, values


def publish(session: Any, targets: Any, payload: Any) -> None:
    document, values = payload
    ports = observed(document, targets)
    if revisions(document, ports) != revisions(session.document, ports):
        raise ObsoleteInputs("Tissue group inputs changed before publication.")
    previous = {key: session.document.object(key).final_result for key in targets}
    changed = {key: accepted(session, document, key, value, ports) for key, value in values.items()}
    session.replace_document(objects=tuple(changed.get(o.id, o) for o in session.document.objects))
    from .tissue_tasks import published

    for key, before in previous.items():
        published(session, key, "final", before)


def accepted(session: Any, document: Any, key: str, output: Any, ports: Any) -> Any:
    item = session.document.object(key)
    asset = tissue_results.register(session, output, "final")
    result = tissue_results.accept(document, item, "final", ports, asset, output)
    return replace(item, **tissue_results.publication(item, "final", result, output))


def completed(session: Any, targets: Any, job: Job, state: str) -> None:
    if state == "failed":
        for key in targets:
            tissue_results.fail(session, key, "final", job.error)
