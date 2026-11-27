"""All skin stages share reservations, dispatch capture, publication and authored undo."""

import json
from dataclasses import replace
from functools import partial
from typing import Any
from uuid import uuid4

from anthroforge.core.jobs import Job, ObsoleteInputs
from anthroforge.core.results import Port
from anthroforge.core.skin import SkinStage
from anthroforge.core.skin_draft import AppliedDraftConfiguration
from anthroforge.native.mesh import NativeCancellation

from . import (
    authored_jobs,
    dependencies,
    skin_checkpoint_assets,
    skin_job_intents,
    skin_stages,
    skin_workloads,
)
from .assets import Asset
from .construction_policy import revisions
from .skin_draft_build import CheckpointFailure
from .skin_results import IncompleteBuild


def build(session: Any, stage: str = "construction") -> str:
    if stage not in skin_stages.POLICIES:
        raise ValueError("Unknown skin build stage.")
    session.skin_status.require("build" if stage == "construction" else stage)
    session.skin_pipeline.explicit(stage)
    intent = skin_job_intents.capture(session, stage)
    return authored_jobs.begin(session, partial(enqueue, session, stage, intent=intent))


def enqueue(session: Any, stage: str, origin: int, intent: Any = None) -> str:
    intent = intent or skin_job_intents.capture(session, stage)
    intent = replace(intent, epoch=session.skin_pipeline.epoch)
    policy = skin_stages.POLICIES[stage]
    job = make_job(session, stage, origin, intent)
    job.cancel = NativeCancellation(session.engine)
    job.retry = retry_callback(session, stage, origin, intent)
    job.restart_on_input_change = not intent.automatic
    job.user_cancelable = not (intent.automatic and "envelope" in policy.outputs)
    job.cleanup = partial(session.skin_pipeline.completed, job, intent)
    configure(job, session, stage, intent)
    return str(session.scheduler.submit(job))


def configure(job: Job, session: Any, stage: str, intent: Any) -> None:
    policy = skin_stages.POLICIES[stage]
    outputs = {Port(str(session.document.id), "skin_" + name) for name in policy.outputs}
    inputs = partial(skin_job_intents.inputs, intent, policy)
    dependencies.renewable_contract(job, session.document, outputs, inputs)
    job.renew_inputs = partial(renew, inputs=inputs)
    job.renew_inputs(job, session.document)


def renew(job: Job, document: Any, inputs: Any) -> None:
    dependencies.renew(job, document, job.provides, inputs)
    job.prerequisites = job.observes


def retry_callback(session: Any, stage: str, origin: int, intent: Any) -> Any:
    if intent.automatic:
        return session.skin_pipeline.retry
    return partial(enqueue, session, stage, origin, intent)


def make_job(session: Any, stage: str, origin: int, intent: Any) -> Job:
    return Job(
        skin_stages.POLICIES[stage].title,
        frozenset((str(session.document.id),)),
        partial(skin_job_intents.prepare, session, intent, stage),
        partial(compute, session.engine, stage, intent),
        partial(publish, session, stage, origin, intent),
        key="skin-" + stage,
        kind="skin_" + stage,
        workload=partial(
            skin_workloads.estimate, session.resources, builder=intent.configuration.builder
        ),
    )


def compute(engine: Any, stage: str, intent: Any, payload: Any, cancel: Any) -> Any:
    document, resources, options = payload
    document = intent.project(document)
    reads = revisions(
        document, skin_job_intents.inputs(intent, skin_stages.POLICIES[stage], document)
    )
    try:
        outputs = skin_stages.POLICIES[stage].compute(engine, document, resources, cancel, options)
        return result_payload(document, outputs, reads)
    except IncompleteBuild as error:
        return result_payload(document, error.stages, reads, str(error))
    except CheckpointFailure as error:
        return document, {}, str(error), error.checkpoints, reads


def result_payload(document: Any, outputs: Any, reads: Any, error: str = "") -> Any:
    checkpoints = tuple(c for output in outputs.values() for c in output.checkpoints)
    return document, outputs, error, checkpoints, reads


def publish(session: Any, stage: str, origin: int, intent: Any, payload: Any) -> None:
    document, outputs, error, checkpoints, reads = payload
    skin_job_intents.require(session, intent, stage)
    policy = skin_stages.POLICIES[stage]
    inputs = partial(skin_job_intents.inputs, intent, policy)
    current = intent.project(session.document)
    if reads != revisions(current, inputs(current)):
        raise ObsoleteInputs("Skin inputs changed before publication.")
    outputs = retained_outputs(document, outputs, error)
    stages = accepted_stages(document, outputs, reads)
    install(session, (stage, origin, intent), outputs, stages, reads, error, checkpoints)
    if error:
        raise ValueError(error)


def accepted_stages(document: Any, outputs: Any, reads: Any) -> Any:
    return {
        name: accepted(document, name, result.data.digest, reads)
        for name, result in outputs.items()
    }


def retained_outputs(document: Any, outputs: Any, error: str) -> Any:
    if error and document.skin.reference and "topology" in outputs:
        outputs = dict(outputs)
        outputs["pending_topology"] = outputs.pop("topology")
    return outputs


def install(
    session: Any, request: Any, outputs: Any, stages: Any, reads: Any, error: str, checkpoints: Any
) -> None:
    stage, origin, intent = request
    retain_resources(session, outputs, stages)
    for bundle in checkpoints:
        session.resources.skin[bundle.asset.digest] = bundle.asset
    proof = publication_proof(session, request, reads)
    applied = applied_configuration(intent, outputs.get("envelope"))
    results = dict(stages=stages, final=outputs.get("final"), error=error, applied=applied)
    merge_result = partial(merge, **results, checkpoints=checkpoints)
    authored_jobs.publish(session, origin, merge_result, proof)


def publication_proof(session: Any, request: Any, reads: Any) -> Any:
    stage, origin, intent = request
    retry = (
        partial(session.skin_pipeline.resume, stage, intent.configuration)
        if intent.automatic
        else retry_callback(session, stage, origin, intent)
    )
    return authored_jobs.Capture(reads, retry, projection=intent.project)


def retain_resources(session: Any, outputs: Any, stages: Any) -> None:
    for name, result in outputs.items():
        session.assets[stages[name].asset] = Asset(result.mesh, "generated", "", 1.0, False)
        session.resources.skin[result.data.digest] = result.data
        if result.reference:
            session.resources.skin[result.reference.digest] = result.reference


def applied_configuration(intent: Any, envelope: Any) -> Any:
    if envelope is None:
        return None
    from .skin_evaluation import BUILDERS

    metadata = json.loads(envelope.data.metadata)
    version = metadata.get("builder_version", BUILDERS[intent.configuration.builder].version)
    return AppliedDraftConfiguration(intent.configuration, version)


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


def merge(
    document: Any,
    stages: Any,
    final: Any = None,
    error: str = "",
    applied: Any = None,
    checkpoints: Any = (),
) -> Any:
    skin = merge_stages(document.skin, stages, error)
    skin = skin_checkpoint_assets.retained(skin, checkpoints)
    if applied is not None:
        skin = replace(skin, applied_draft=applied, migration_draft=None)
    if final is not None and final.reference is not None:
        skin = completed_reference(skin, final, stages)
    return replace(document, skin=retain_pending_configuration(skin))


def merge_stages(skin: Any, stages: Any, error: str) -> Any:
    stale = bool(skin.reference if "topology" in stages else skin.topology.asset)
    return replace(skin, **stages, construction_stale=stale, build_error=error)


def retain_pending_configuration(skin: Any) -> Any:
    applied = skin.applied_draft
    pending = bool(applied and skin.draft_settings.configuration() != applied.configuration)
    return replace(skin, construction_stale=skin.construction_stale or pending)


def completed_reference(skin: Any, final: Any, stages: Any) -> Any:
    topology = stages.get(
        "topology", skin.pending_topology if skin.pending_topology.asset else skin.topology
    )
    return replace(
        skin,
        reference=final.reference.digest,
        reference_sources=final.sources,
        topology=topology,
        pending_topology=SkinStage(),
        construction_stale=False,
        fits=tuple(replace(fit, stale=True) for fit in skin.fits),
    )
