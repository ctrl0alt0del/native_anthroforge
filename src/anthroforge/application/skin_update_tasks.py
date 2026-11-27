"""Automatic final-skin output participates in the existing coordinator fan-out."""

import json
from dataclasses import replace
from functools import partial
from typing import Any

from anthroforge.core import skin_sources
from anthroforge.core.jobs import Job, ObsoleteInputs
from anthroforge.core.results import Port
from anthroforge.core.skin_pipeline import RepairRequired
from anthroforge.native.mesh import NativeCancellation

from . import (
    dependencies,
    skin_deformation_evaluation,
    skin_inputs,
    skin_job_intents,
    skin_jobs,
    skin_workloads,
)
from .assets import Asset
from .construction_policy import revisions


def evaluate(session: Any) -> str:
    if not skin_sources.contributors(session.document):
        raise ValueError("No contributing anatomy for skin evaluation.")
    return str(session.skin_pipeline.evaluate())


def inputs(resources: Any, document: Any) -> set[Port]:
    reference = resources.skin.get(document.skin.reference)
    policy = json.loads(reference.metadata)["tissue_surface"] if reference else "FINISHED"
    ports = {
        Port(str(document.id), n)
        for n in ("skin_scope", "skin_reference", "skin_deformation_settings")
    }
    for row in skin_sources.contributors(document):
        ports.update(skin_inputs.source_ports(row))
        if row.kind == "TISSUE" and policy == "INFLATED_REST":
            ports.discard(Port(row.owner, "final"))
            ports.add(Port(row.owner, "rest"))
    return dependencies.closure(dependencies.graph(document), ports)


def request(session: Any, interactive: bool = False, intent: Any = None) -> str:
    skin_deformation_evaluation.reference(session.document, session.resources)
    intent = intent or skin_job_intents.capture(session, "deformation", True)
    job = make_job(session, intent)
    job.cancel = NativeCancellation(session.engine)
    job.interactive = interactive
    job.publish_during_edit = interactive
    job.retry = session.skin_pipeline.retry
    job.cleanup = partial(completed, session, job, intent)
    configure(job, session)
    return str(session.scheduler.submit(job))


def configure(job: Job, session: Any) -> None:
    ports = {Port(str(session.document.id), "skin_final")}
    observe = partial(inputs, session.resources)
    dependencies.renewable_contract(job, session.document, ports, observe)
    job.renew_inputs = partial(renew, observe=observe)
    job.renew_inputs(job, session.document)


def renew(job: Job, document: Any, observe: Any) -> None:
    dependencies.renew(job, document, job.provides, observe)
    job.prerequisites = job.observes


def make_job(session: Any, intent: Any) -> Job:
    return Job(
        "Update skin",
        frozenset((str(session.document.id),)),
        lambda doc: (intent.project(doc), session.resources.snapshot()),
        partial(compute, session.engine),
        partial(publish, session, intent),
        key="skin-update",
        kind="skin_deformation",
        workload=partial(skin_workloads.estimate, session.resources),
    )


def compute(engine: Any, payload: Any, cancel: Any) -> Any:
    document, resources = payload
    try:
        return document, skin_deformation_evaluation.evaluate(
            engine, document, resources, cancel.handle
        )
    except RepairRequired as repair:
        return document, repair


def publish(session: Any, intent: Any, payload: Any) -> None:
    document, output = payload
    skin_job_intents.require(session, intent, "deformation")
    reads = revisions(document, inputs(session.resources, document))
    if reads != revisions(session.document, inputs(session.resources, session.document)):
        raise ObsoleteInputs("Skin anatomical inputs changed before publication.")
    if isinstance(output, RepairRequired):
        session.skin_pipeline.repair = output.stage
        session.skin_pipeline.reason = str(output)
        return
    install(session, document, output, reads)


def install(session: Any, document: Any, output: Any, reads: Any) -> None:
    skin = session.document.skin
    stage = replace(
        skin_jobs.accepted(document, "final", output.data.digest, reads),
        revision=skin.final.revision + 1,
    )
    session.assets[stage.asset] = Asset(output.mesh, "generated", "", 1.0, False)
    session.resources.skin[output.data.digest] = output.data
    session.replace_document(skin=replace(skin, final=stage))


def completed(session: Any, job: Job, intent: Any, state: str) -> None:
    session.skin_pipeline.completed(job, intent, state)
    if intent.epoch != session.skin_pipeline.epoch:
        return
    if state == "failed":
        skin = session.document.skin
        result = replace(skin.final, status="failed", error=job.error)
        session.replace_document(skin=replace(skin, final=result))


def edited(session: Any, seeds: set[Port]) -> None:
    session.skin_pipeline.changed()


def pending(session: Any, released: bool = False) -> None:
    session.skin_pipeline.changed()
