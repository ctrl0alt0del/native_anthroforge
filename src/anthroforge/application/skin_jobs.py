"""Document skin jobs use the shared reservations, provenance and authored undo boundary."""

from dataclasses import replace
from functools import partial
from typing import Any
from uuid import uuid4

from anthroforge.core.jobs import Job, ObsoleteInputs
from anthroforge.core.results import Port
from anthroforge.core.skin import SkinStage
from anthroforge.native.mesh import NativeCancellation

from . import authored_jobs, dependencies, skin_evaluation, skin_inputs
from .assets import Asset
from .construction_policy import revisions


def build_envelope(session: Any) -> str:
    return authored_jobs.begin(session, partial(enqueue, session))


def enqueue(session: Any, origin: int) -> str:
    job = make_job(session, origin)
    job.cancel = NativeCancellation(session.engine)
    job.retry = partial(enqueue, session, origin)
    job.restart_on_input_change = True
    output = {Port(str(session.document.id), "skin_envelope")}
    dependencies.renewable_contract(job, session.document, output, skin_inputs.envelope)
    job.renew_inputs = renew
    renew(job, session.document)
    return str(session.scheduler.submit(job))


def renew(job: Job, document: Any) -> None:
    dependencies.renew(job, document, job.provides, skin_inputs.envelope)
    job.prerequisites = job.observes


def make_job(session: Any, origin: int) -> Job:
    return Job(
        "Build skin envelope",
        frozenset((str(session.document.id),)),
        lambda document: (document, session.resources.snapshot()),
        partial(compute, session),
        partial(publish, session, origin),
        key="skin-envelope",
        kind="skin_envelope",
    )


def compute(session: Any, payload: Any, cancel: Any) -> Any:
    document, resources = payload
    return document, skin_evaluation.evaluate(session.engine, document, resources, cancel.handle)


def publish(session: Any, origin: int, payload: Any) -> None:
    document, output = payload
    reads = revisions(document, skin_inputs.envelope(document))
    if reads != revisions(session.document, skin_inputs.envelope(session.document)):
        raise ObsoleteInputs("Skin sources changed before envelope publication.")
    key, data = str(uuid4()), output.data
    stage = accepted(document, key, data.digest, reads)
    proof = authored_jobs.Capture(reads, partial(enqueue, session, origin))
    authored_jobs.publish(session, origin, partial(merge, stage=stage), proof)
    session.assets[key] = Asset(output.mesh, "generated", "", 1.0, False)
    session.resources.skin[data.digest] = data


def accepted(document: Any, key: str, data: str, reads: Any) -> SkinStage:
    owners = {read.owner for read in reads}
    pending = tuple(
        item.id
        for item in (*document.entities, *document.objects)
        if item.id in owners and item.result.status == "pending"
    )
    return SkinStage(
        asset=key,
        data=data,
        revision=document.skin.envelope.revision + 1,
        authored_revision=document.skin.revision,
        inputs=reads,
        pending=pending,
    )


def merge(document: Any, stage: SkinStage) -> Any:
    skin = replace(
        document.skin, envelope=stage, construction_stale=bool(document.skin.topology.asset)
    )
    return replace(document, skin=skin)
