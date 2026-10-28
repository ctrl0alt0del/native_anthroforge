"""Coordinated, isolated fitting publishes one independent result into its initiating undo."""

from dataclasses import dataclass, replace
from functools import partial
from typing import Any
from uuid import uuid4

from anthroforge.core.jobs import Job, ObsoleteInputs
from anthroforge.core.results import Port
from anthroforge.core.skin import FittedShortcut
from anthroforge.core.skin_fitting import Settings
from anthroforge.native.mesh import NativeCancellation

from . import (
    authored_jobs,
    dependencies,
    skin_fit_capture,
    skin_fit_evaluation,
    skin_fit_results,
    skin_update_tasks,
    skin_workloads,
)
from .assets import Asset
from .construction_policy import revisions


def definitions(document: Any) -> tuple[Any, ...]:
    return (
        document.shortcuts,
        document.driving_shortcuts,
        document.attachments_enabled,
        document.update_mode,
    )


@dataclass(frozen=True)
class Capture(authored_jobs.Capture):
    definitions: tuple[Any, ...]

    def matches(self, document: Any) -> bool:
        return super().matches(document) and self.definitions == definitions(document)


def start(session: Any, shortcut: str, settings: dict[str, Any], authoring: bool = False) -> str:
    skin_fit_capture.eligible(session, shortcut)
    options = Settings(**settings)
    if options.strategy != "SCALE_AWARE" and not authoring:
        raise ValueError("Single Active is available only through the authoring fitting operation.")
    return authored_jobs.begin(session, partial(enqueue, session, shortcut, options, str(uuid4())))


def inputs(session: Any, document: Any) -> set[Port]:
    return skin_update_tasks.inputs(session.resources, document) | {
        Port(str(document.id), "skin_final"),
        *(Port(item.id, "driver") for item in document.driving_shortcuts),
    }


def enqueue(session: Any, shortcut: str, settings: Settings, identity: str, origin: int) -> str:
    job = make_job(session, shortcut, settings, identity, origin)
    job.cancel = NativeCancellation(session.engine)
    job.retry = partial(enqueue, session, shortcut, settings, identity, origin)
    job.restart_on_input_change = True
    provides = {Port(str(session.document.id), "skin_fit:" + identity)}
    dependencies.renewable_contract(job, session.document, provides, partial(inputs, session))
    job.renew_inputs = partial(renew, session=session)
    job.renew_inputs(job, session.document)
    return str(session.scheduler.submit(job))


def renew(job: Job, document: Any, session: Any) -> None:
    dependencies.renew(job, document, job.provides, partial(inputs, session))
    job.prerequisites = job.observes


def make_job(session: Any, shortcut: str, settings: Settings, identity: str, origin: int) -> Job:
    return Job(
        "Fit shortcut to bones",
        frozenset((str(session.document.id),)),
        partial(capture, session, shortcut, settings),
        partial(compute, session.engine),
        partial(publish, session, identity, origin),
        key="skin-fit:" + shortcut,
        kind="skin_fit",
        workload=partial(skin_workloads.estimate, session.resources),
    )


def capture(session: Any, shortcut: str, settings: Settings, document: Any) -> Any:
    return document, session.resources.snapshot(), session.preferences.value, shortcut, settings


def compute(engine: Any, payload: Any, cancel: Any) -> Any:
    return payload, skin_fit_evaluation.evaluate(engine, payload, cancel)


def publish(session: Any, identity: str, origin: int, result: Any) -> None:
    payload, output = result
    document, _, _, shortcut, settings = payload
    restart = partial(enqueue, session, shortcut, settings, identity, origin)
    proof = Capture(revisions(document, inputs(session, document)), restart, definitions(document))
    if not proof.matches(session.document):
        raise ObsoleteInputs("Fitting source changed before publication.")
    asset = str(uuid4())
    session.assets[asset] = Asset(output.mesh, "generated", "", 1.0, False)
    session.resources.skin[output.data.digest] = output.data
    item = fitted(document, identity, shortcut, asset, output.data.digest, proof.reads)
    authored_jobs.publish(session, origin, partial(append, item=item), proof)


def append(document: Any, item: FittedShortcut) -> Any:
    fits = tuple(f for f in document.skin.fits if f.id != item.id) + (item,)
    return replace(document, skin=replace(document.skin, fits=fits))


def fitted(document: Any, identity: str, shortcut: str, asset: str, data: str, reads: Any) -> Any:
    return FittedShortcut(
        identity,
        shortcut,
        asset,
        data,
        document.revision,
        inputs=reads,
        definitions=skin_fit_results.definition_key(document),
    )
