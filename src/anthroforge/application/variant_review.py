"""One cancellable variant review per editing context, owned by the shared coordinator."""

from dataclasses import replace
from functools import partial
from time import monotonic, sleep
from typing import Any
from uuid import uuid4

from anthroforge.core.jobs import ObsoleteInputs
from anthroforge.core.reconstruction import SceneSnapshot, Variant
from anthroforge.core.skeleton_update import require_review
from anthroforge.native.mesh import NativeCancellation

from . import skeleton_operations, variant_operations, variant_preparation
from .assembly_candidate import readset
from .assembly_runtime import Assembly, State, completed
from .editing_contexts import bare


class VariantReview:
    def __init__(self, session: Any) -> None:
        self.session, self.runtime = session, Assembly(session)
        self.request: Any = None
        self.accepted: Any = None
        self.accepted_reads: Any = None

    def prepare(self, variant: str, mode: str = "promote", **options: Any) -> dict[str, Any]:
        variant_operations.require_idle(self.session)
        if mode not in {"promote", "refresh"}:
            raise ValueError("Choose Promote or Refresh supports.")
        self.runtime.cancel_preparation()
        self.session.contexts.flush()
        self.capture_request(variant, mode, options)
        value = State(str(uuid4()), state="preparing", document=str(self.session.document.id))
        self.runtime.preparation = value
        self.submit(value)
        return self.status()

    def capture_request(self, key: str, mode: str, options: Any) -> None:
        value = variant_operations.state(self.session)
        record = value.variant(key)
        if record.checkpoint:
            raise ValueError("Fork a checkpoint before refreshing or promoting it.")
        self.request = (
            record,
            value.snapshot(record.baseline),
            value.snapshot(record.current),
            mode,
            options,
        )
        self.accepted = self.session.contexts.scene("")

    def submit(self, value: State) -> None:
        s = self.session
        worker = partial(variant_preparation.prepare, s.engine, s.profiler, self.request)
        job = self.runtime.job(value, worker, "skeleton_prepare")
        job.label = "Review variant " + self.request[3]
        job.prepare = self.capture
        job.publish = partial(self.publish, value)
        job.cancel = NativeCancellation(s.engine)
        job.cleanup = partial(completed, value, job)
        value.job = job.id
        s.scheduler.submit(job)

    def capture(self, document: Any) -> Any:
        return self.accepted, self.session.resources.snapshot(), self.session.preferences.value

    def publish(self, value: State, candidate: Any) -> None:
        if self.runtime.preparation is not value:
            raise ObsoleteInputs("Variant review was replaced.")
        self.accepted_reads = readset(
            self.accepted, {k for k, _ in candidate.reads.records.records}
        )
        self.validate(candidate)
        value.candidate, value.state = candidate, "ready"

    def validate(self, candidate: Any) -> None:
        record, _, captured, mode, _ = self.request
        current = variant_operations.state(self.session)
        if current.variant(record.id) != record or current.snapshot(record.current) != captured:
            raise ObsoleteInputs("The variant changed; review again.")
        accepted = self.session.contexts.scene("")
        self.accepted_reads.require(accepted)
        candidate.reads.require(captured if mode == "refresh" else accepted)

    def status(self, wait: bool = False, timeout: float = 300.0) -> dict[str, Any]:
        if wait:
            self.wait(timeout)
        value = self.runtime.preparation
        if value.state == "ready":
            try:
                self.validate(value.candidate)
            except (ValueError, ObsoleteInputs) as error:
                value.state, value.error = "stale", str(error)
        return self.describe()

    def describe(self) -> dict[str, Any]:
        from .skeleton_runtime import details

        value = self.runtime.preparation
        return dict(
            token=value.token,
            state=value.state,
            error=value.error,
            job_id=value.job,
            mode=self.request[3] if self.request else "",
            **details(value.candidate),
        )

    def wait(self, timeout: float) -> None:
        deadline = monotonic() + timeout
        while self.runtime.preparation.state == "preparing":
            self.session.scheduler.tick()
            if monotonic() >= deadline:
                raise TimeoutError("Variant preparation is still running.")
            sleep(0.002)

    def apply(self, token: str, approved: list[str] | None = None) -> Any:
        variant_operations.require_idle(self.session)
        value = self.runtime.preparation
        if value.token != token or value.state != "ready":
            raise ValueError("Wait for a current variant review.")
        self.validate(value.candidate)
        require_review(value.candidate.findings, approved or [])
        result = adopt(self.session, self.request, value.candidate)
        self.runtime.cancel_preparation()
        return result

    def cancel(self) -> None:
        self.runtime.cancel()
        self.request, self.accepted, self.accepted_reads = None, None, None


def adopt(session: Any, request: Any, candidate: Any) -> Any:
    record, _, _, mode, _ = request
    if mode == "refresh":
        return refresh(session, record, candidate)
    with session.contexts.use(""):
        updated = candidate.merge(session.document)
        record_state = previous_checkpoint(session, record)
        install(session, candidate, updated, record_state)
    return dict(promoted=record.id, checkpoint=record_state.variants[-1].id)


def install(session: Any, candidate: Any, updated: Any, records: Any = None) -> None:
    session.begin()
    try:
        skeleton_operations.adopt_reviewed(session, candidate, updated)
        if records is not None:
            session.replace_document(reconstruction=records)
        session.commit()
    except Exception:
        session.cancel()
        raise


def previous_checkpoint(session: Any, variant: Any) -> Any:
    state = variant_operations.state(session)
    snapshot = SceneSnapshot(bare(session.document))
    row = Variant(
        "Before promoting " + variant.name,
        variant.subjects,
        variant.subjects,
        snapshot.id,
        snapshot.id,
        checkpoint=True,
    )
    return replace(state, snapshots=(*state.snapshots, snapshot), variants=(*state.variants, row))


def refresh(session: Any, record: Any, candidate: Any) -> Any:
    if record.id not in session.contexts.states:
        session.contexts.add(record.id, candidate.baseline)
    with session.contexts.use(record.id):
        install(session, candidate, candidate.document)
    return dict(refreshed=record.id)
