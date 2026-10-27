"""Read-only fitted playback owns transient geometry outside document/history resources."""

from dataclasses import dataclass
from functools import partial
from math import isfinite
from typing import Any
from uuid import uuid4

from anthroforge.core.jobs import Job, ObsoleteInputs
from anthroforge.core.scheduling import Workload
from anthroforge.native import construction, skin_fit_playback, topology
from anthroforge.native.mesh import NativeCancellation

from . import previews, skin_fit_results


@dataclass(frozen=True)
class Candidate:
    identity: str
    data: str
    value: float
    mesh: Any


def request(session: Any, identity: str, value: float) -> dict[str, Any]:
    if not isfinite(value):
        raise ValueError("Preview value must be finite.")
    item = skin_fit_results.selected(session, identity)
    previous = displayed(session)
    previews.cancel(session, "skin_fit_preview")
    state = previews.Preview[Candidate](str(uuid4()), identity, str(session.document.id))
    state.asset = previous if previous and previous.identity == identity else None
    state.state = "queued"
    session.skin_fit_preview = state
    job = make_job(session, state, item, value)
    state.job = str(session.scheduler.submit(job))
    return status(session)


def make_job(session: Any, state: Any, item: Any, value: float) -> Job:
    job = Job(
        "Preview fitted skin",
        frozenset(),
        partial(capture, session, item),
        partial(compute, value),
        partial(publish, session, state),
        key="skin-fit-preview",
        kind="skin_fit_preview",
        writes=False,
        interactive=True,
        publish_during_edit=True,
    )
    return configure_job(session, state, item, job)


def configure_job(session: Any, state: Any, item: Any, job: Job) -> Job:
    mesh = session.assets[item.reference].mesh
    job.workload = lambda _: Workload(candidates=mesh.counts[0], triangles=mesh.counts[1])
    job.cancel = NativeCancellation(session.engine)
    job.cleanup = partial(completed, state, job)
    return job


def capture(session: Any, item: Any, document: Any) -> Any:
    if item not in document.skin.fits:
        raise ObsoleteInputs("Fitted result was removed.")
    return item, session.assets[item.reference].mesh, session.resources.skin[item.data]


def compute(value: float, payload: Any, cancel: Any) -> Candidate:
    item, reference, data = payload
    positions = skin_fit_playback.evaluate(reference.engine, data.arrays, value, cancel.handle)
    draft = construction.deformed(reference, positions, cancel.handle)
    mesh = topology.finalize(draft, reference, cancel.handle)
    return Candidate(item.id, item.data, value, mesh)


def publish(session: Any, state: Any, candidate: Candidate) -> None:
    if session.skin_fit_preview is not state or not valid(session, state, candidate):
        raise ObsoleteInputs("Fitted preview was superseded.")
    state.asset, state.state = candidate, "ready"


def valid(session: Any, state: Any, candidate: Candidate) -> bool:
    return str(session.document.id) == state.document and any(
        f.id == candidate.identity and f.data == candidate.data for f in session.document.skin.fits
    )


def displayed(session: Any) -> Candidate | None:
    state = session.skin_fit_preview
    return state.asset if state.asset and valid(session, state, state.asset) else None


def completed(state: Any, job: Job, result: str) -> None:
    if result != "succeeded":
        state.state, state.error = result, job.error


def status(session: Any) -> dict[str, Any]:
    state, candidate = session.skin_fit_preview, displayed(session)
    return dict(
        state=state.state,
        error=state.error,
        job_id=state.job,
        identity=state.target,
        visible=candidate is not None,
        value=candidate.value if candidate else None,
    )


def cancel(session: Any) -> None:
    previews.cancel(session, "skin_fit_preview")
