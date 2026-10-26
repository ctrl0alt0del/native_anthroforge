"""All skin stages share reservations, dispatch capture, publication and authored undo."""

from dataclasses import replace
from functools import partial
from typing import Any
from uuid import uuid4

from anthroforge.core.jobs import Job, ObsoleteInputs
from anthroforge.core.results import Port
from anthroforge.core.skin import SkinStage
from anthroforge.native.mesh import NativeCancellation

from . import authored_jobs, dependencies, skin_stages, skin_workloads
from .assets import Asset
from .construction_policy import revisions


def build(session: Any, stage: str = "construction") -> str:
    if stage not in skin_stages.POLICIES:
        raise ValueError("Unknown skin build stage.")
    return authored_jobs.begin(session, partial(enqueue, session, stage))


def enqueue(session: Any, stage: str, origin: int) -> str:
    policy = skin_stages.POLICIES[stage]
    job = make_job(session, stage, origin)
    job.cancel = NativeCancellation(session.engine)
    job.retry = partial(enqueue, session, stage, origin)
    job.restart_on_input_change = True
    outputs = {Port(str(session.document.id), "skin_" + name) for name in policy.outputs}
    dependencies.renewable_contract(job, session.document, outputs, policy.inputs)
    job.renew_inputs = partial(renew, policy=policy)
    job.renew_inputs(job, session.document)
    return str(session.scheduler.submit(job))


def renew(job: Job, document: Any, policy: Any) -> None:
    dependencies.renew(job, document, job.provides, policy.inputs)
    job.prerequisites = job.observes


def make_job(session: Any, stage: str, origin: int) -> Job:
    return Job(
        skin_stages.POLICIES[stage].title,
        frozenset((str(session.document.id),)),
        lambda document: (document, session.resources.snapshot()),
        partial(compute, session, stage),
        partial(publish, session, stage, origin),
        key="skin-" + stage,
        kind="skin_" + stage,
        workload=partial(skin_workloads.estimate, session.resources),
    )


def compute(session: Any, stage: str, payload: Any, cancel: Any) -> Any:
    document, resources = payload
    return document, skin_stages.POLICIES[stage].compute(
        session.engine, document, resources, cancel
    )


def publish(session: Any, stage: str, origin: int, payload: Any) -> None:
    document, outputs = payload
    policy = skin_stages.POLICIES[stage]
    reads = revisions(document, policy.inputs(document))
    if reads != revisions(session.document, policy.inputs(session.document)):
        raise ObsoleteInputs("Skin inputs changed before publication.")
    stages = {
        name: accepted(document, name, result.data.digest, reads)
        for name, result in outputs.items()
    }
    proof = authored_jobs.Capture(reads, partial(enqueue, session, stage, origin))
    authored_jobs.publish(session, origin, partial(merge, stages=stages), proof)
    for name, result in outputs.items():
        session.assets[stages[name].asset] = Asset(result.mesh, "generated", "", 1.0, False)
        session.resources.skin[result.data.digest] = result.data


def accepted(document: Any, name: str, data: str, reads: Any) -> SkinStage:
    return SkinStage(
        asset=str(uuid4()),
        data=data,
        revision=getattr(document.skin, name).revision + 1,
        authored_revision=document.skin.revision,
        inputs=reads,
        pending=pending(document, reads),
    )


def pending(document: Any, reads: Any) -> tuple[str, ...]:
    owners = {read.owner for read in reads}
    return tuple(
        item.id
        for item in (*document.entities, *document.objects)
        if item.id in owners and item.result.status == "pending"
    )


def merge(document: Any, stages: Any) -> Any:
    stale = (
        bool(document.skin.reference)
        if "topology" in stages
        else bool(document.skin.topology.asset)
    )
    skin = replace(document.skin, **stages, construction_stale=stale)
    return replace(document, skin=skin)
