"""Skeleton update lifecycle composes the existing pinned-project preparation runtime."""

from dataclasses import asdict
from functools import partial
from time import monotonic, sleep
from typing import Any
from uuid import uuid4

from anthroforge.native.mesh import NativeCancellation

from . import skeleton_control_review, skeleton_matching, skeleton_preparation
from .assembly_runtime import Assembly, State


class SkeletonUpdate:
    def __init__(self, session: Any) -> None:
        self.session = session
        self.runtime = Assembly(session)
        self.inventory_key: Any = None
        self.inventory_rows: list[dict[str, Any]] = []

    def inspect(self, path: str) -> dict[str, Any]:
        self.runtime.inspect(path)
        return self.status()

    def prepare(self, source: str, matches: Any = None, **options: Any) -> dict[str, Any]:
        runtime = self.runtime
        if source != runtime.source.token or runtime.source.state != "ready":
            raise ValueError("Inspect a replacement project before preparing an update.")
        runtime.cancel_preparation()
        value = State(str(uuid4()), state="preparing", document=runtime.source.document)
        runtime.preparation = value
        self.submit(value, self.worker(dict(options, matches=matches or {})))
        return self.status()

    def worker(self, options: Any) -> Any:
        return partial(
            skeleton_preparation.prepare,
            self.runtime.source.source,
            options,
            self.session.engine,
            self.session.profiler,
        )

    def submit(self, value: State, worker: Any) -> None:
        from .assembly_runtime import completed

        job = self.runtime.job(value, worker, "skeleton_prepare")
        job.label = "Compare replacement skeleton and dependent anatomy"
        job.prepare = self.capture
        job.cancel = NativeCancellation(self.session.engine)
        job.cleanup = partial(completed, value, job)
        value.job = job.id
        self.session.scheduler.submit(job)

    def capture(self, document: Any) -> Any:
        return document, self.session.resources.snapshot(), self.session.preferences.value

    def ready(self, token: str) -> Any:
        return self.runtime.ready(token)

    def cancel(self) -> None:
        self.runtime.cancel()

    def status(self, wait: bool = False, timeout: float = 300.0) -> dict[str, Any]:
        if wait:
            self.wait(timeout)
        return describe(self)

    def wait(self, timeout: float) -> None:
        deadline = monotonic() + timeout
        while any(
            v.state in ("loading", "preparing")
            for v in (self.runtime.source, self.runtime.preparation)
        ):
            self.session.scheduler.tick()
            if monotonic() >= deadline:
                raise TimeoutError("Skeleton update preparation is still running.")
            sleep(0.002)


def describe(service: SkeletonUpdate) -> dict[str, Any]:
    source, state = service.runtime.source, service.runtime.preparation
    return dict(
        source=source.token,
        source_state=source.state,
        source_error=source.error,
        token=state.token,
        state=state.state,
        error=state.error,
        job_id=state.job or source.job,
        inventory=inventory(service),
        **details(state.candidate),
    )


def inventory(service: SkeletonUpdate) -> Any:
    source = service.runtime.source.source
    key = (id(source), service.session.document.entities, service.session.document.imports)
    if key != service.inventory_key:
        service.inventory_key = key
        service.inventory_rows = (
            skeleton_matching.inventory(source.document, service.session.document) if source else []
        )
    return service.inventory_rows


def details(candidate: Any) -> dict[str, Any]:
    if candidate is None:
        return {}
    return dict(
        ready=candidate.ready,
        findings=[asdict(v) for v in candidate.findings],
        changes=[asdict(v) for v in candidate.changes],
        evidence=candidate.evidence,
        comparison=candidate.comparison,
        skin=candidate.skin,
        identities=candidate.identities,
        mappings=candidate.mappings,
        required=candidate.required,
        controls=skeleton_control_review.rows(candidate.baseline),
    )
