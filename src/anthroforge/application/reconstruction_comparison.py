"""Read-only frozen comparisons on the existing coordinator; no scene adoption."""

from functools import partial
from time import monotonic, sleep
from typing import Any

from anthroforge.core.jobs import Job
from anthroforge.native import comparison, sections, topology
from anthroforge.native.mesh import NativeCancellation

from . import reconstruction_views as views
from .previews import Preview, completed


class Comparison:
    def __init__(self, session: Any) -> None:
        self.session, self.pair = session, None
        self.value: Any = None
        self.project, self.resources = None, None

    def start(self, subject: str, before: Any, after: Any, plane: Any = None) -> Any:
        pair = tuple(
            views.capture(self.session, subject, **selection) for selection in (before, after)
        )
        self.cancel()
        self.retain(pair)
        value = Preview[Any](target=subject, state="queued")
        self.value = value
        job = self.job(value, pair, plane)
        value.job = job.id
        self.session.scheduler.submit(job)
        return self.status()

    def retain(self, pair: Any) -> None:
        self.pair = pair
        self.project = self.session.contexts.project()
        self.resources = self.session.resources.snapshot()

    def job(self, value: Any, pair: Any, plane: Any) -> Job:
        job = Job(
            "Compare reconstruction stages",
            frozenset(),
            lambda _: pair,
            partial(compute, plane),
            partial(self.publish, value),
            writes=False,
            publish_during_edit=True,
            kind="tissue_inspection",
            cancel=NativeCancellation(self.session.engine),
        )
        job.cleanup = partial(completed, value, job)
        return job

    def publish(self, value: Any, result: Any) -> None:
        if self.value is not value:
            raise ValueError("Comparison replaced.")
        value.asset, value.state = result, "ready"

    def status(self, wait: bool = False, timeout: float = 300) -> Any:
        if wait:
            self.wait(timeout)
        value = self.value
        if value is None:
            return dict(state="idle")
        return dict(
            state=value.state, job_id=value.job, error=value.error, report=value.asset or {}
        )

    def wait(self, timeout: float) -> None:
        deadline = monotonic() + timeout
        while self.value and self.value.state in ("queued", "running"):
            self.session.scheduler.tick()
            if monotonic() > deadline:
                raise TimeoutError("Comparison still running.")
            sleep(0.002)

    def cancel(self) -> None:
        if self.value:
            self.session.scheduler.cancel_job(self.value.job, obsolete=True)
        self.value, self.pair = None, None
        self.project, self.resources = None, None


def compute(plane: Any, pair: Any, cancel: Any) -> Any:
    result = dict(before=views.report(pair[0]), after=views.report(pair[1]), plane=plane)
    if all(len(v.layers) == 1 and v.layers[0].kind == "MESH" for v in pair):
        a, b = (v.layers[0] for v in pair)
        verified = a.lineage is not None and a.lineage == b.lineage
        verified = verified and topology.same_topology(a.resource, b.resource, cancel.handle)
        result["distances"] = comparison.distances(
            a.resource, a.frame, b.resource, b.frame, verified, cancel.handle
        )
    if plane:
        result["sections"] = [section(v, plane, cancel.handle) for v in pair]
    return result


def section(view: Any, plane: Any, cancel: int) -> Any:
    return [
        dict(id=entry.identity, **sections.contours(entry.resource, entry.frame, plane, cancel))
        for entry in view.layers
        if entry.kind == "MESH"
    ]


def execute(session: Any, operation: str, arguments: Any) -> Any:
    from .reconstruction_export import export

    service = session.reconstruction_comparison
    commands = dict(
        start=service.start,
        status=service.status,
        cancel=service.cancel,
        options=partial(views.options, session),
        export=partial(export, session),
    )
    name = operation.removeprefix("reconstruction.compare.")
    if name not in commands:
        raise ValueError("Unknown reconstruction comparison operation.")
    return commands[name](**arguments)
