"""Read-only tissue inspection jobs; presentation never publishes anatomical results."""

from dataclasses import dataclass, field
from functools import partial
from typing import Any

from anthroforge.core.jobs import Job
from anthroforge.core.scheduling import Workload
from anthroforge.native import inspection as native
from anthroforge.native.mesh import NativeCancellation

from . import tissue_inspection_stages as stages
from .inspection_context import freeze
from .inspection_queries import definition
from .previews import Preview, completed


@dataclass
class Inspection:
    values: dict[str, Preview[Any]] = field(default_factory=dict)


def start(session: Any, kind: str, target: str, **options: Any) -> dict[str, Any]:
    stage = options.get("stage", "final")
    options = dict(options, stage=stage)
    definition(kind).validate(session, target, options)
    cancel(session, kind)
    value = Preview[Any](target=target, document=str(session.document.id), state="queued")
    session.tissue_inspection.values[kind] = value
    job = make_job(session, value, kind, options)
    value.job = job.id
    session.scheduler.submit(job)
    return status(session, kind)


def make_job(session: Any, value: Any, kind: str, options: Any) -> Job:
    job = inspection_job(session, value, kind, options)
    job.cancel = NativeCancellation(session.engine)
    job.cleanup = partial(completed, value, job)
    job.workload = lambda _: definition(kind).workload(session, value.target, options)
    return job


def inspection_job(session: Any, value: Any, kind: str, options: Any) -> Job:
    job = Job(
        "Inspect tissue " + kind,
        frozenset(),
        partial(capture, session, value, kind, options),
        partial(compute, kind, options),
        partial(publish, session, value, kind),
        key="tissue_inspection:" + kind,
        kind="tissue_inspection",
        writes=False,
        priority=-5,
        publish_during_edit=True,
    )
    return job


def capture(session: Any, value: Any, kind: str, options: Any, document: Any) -> Any:
    value.state = "running"
    context = freeze(session)
    return context, value.target, definition(kind).signature(context, value.target, options)


def validate(context: Any, target: str, options: Any) -> None:
    stages.mesh(context, target, options["stage"])


def workload(context: Any, target: str, options: Any) -> Workload:
    return Workload(triangles=stages.mesh(context, target, options["stage"]).counts[3])


def expected_asset(context: Any, target: str, options: Any) -> None:
    expected = options.get("expected_asset")
    if (
        expected
        and stages.result(stages.tissue(context, target), options["stage"]).asset != expected
    ):
        raise ValueError("The displayed inspection surface changed. Pick the current stage again.")


def signature(context: Any, target: str, options: Any) -> Any:
    expected_asset(context, target, options)
    selected = {options["stage"], options.get("reference", options["stage"])}
    return tuple(stages.signature(context, target, stage) for stage in sorted(selected))


def compute(kind: str, options: Any, captured: Any, cancellation: Any) -> Any:
    context, target, stamp = captured
    result = definition(kind).compute(context, target, options, cancellation.handle)
    return context, target, options, stamp, result


def comparison(context: Any, target: str, options: Any, cancel: int) -> dict[str, Any]:
    reference, stage = options.get("reference", "rest"), options["stage"]
    stages.compatible(stages.tissue(context, target), reference, stage)
    first, second = stages.mesh(context, target, reference), stages.mesh(context, target, stage)
    output = native.Comparison(
        first,
        second,
        reference == "base" and stage != "base",
        cancel,
        stages.frame(context, stages.tissue(context, target), stage),
    )
    return dict(resource=output, report=comparison_report(output, reference, stage))


def comparison_report(output: Any, reference: str, stage: str) -> dict[str, Any]:
    return dict(
        reference=reference,
        stage=stage,
        minimum=output.stats[0],
        maximum=output.stats[1],
        mean=output.stats[2],
        rms=output.stats[3],
        samples=output.samples,
        units="metres",
        method="material correspondence; vertex-weighted statistics",
    )


def publish(session: Any, value: Any, kind: str, payload: Any) -> None:
    context, target, options, stamp, result = payload
    if (
        session.tissue_inspection.values.get(kind) is not value
        or definition(kind).signature(session, target, options) != stamp
    ):
        raise ValueError("Tissue inspection inputs changed; inspect the accepted stages again.")
    value.asset = dict(result, stamp=stamp, options=options, target=target, kind=kind)
    value.state = "ready"


def status(session: Any, kind: str) -> dict[str, Any]:
    value = session.tissue_inspection.values.get(kind)
    if value is None:
        return dict(state="idle")
    state = value.state
    if value.asset and not current(session, value.asset):
        state = "stale"
    return dict(
        state=state,
        job=value.job,
        target=value.target,
        error=value.error,
        report=value.asset.get("report", {}) if value.asset else {},
    )


def current(session: Any, asset: Any) -> bool:
    try:
        query = definition(asset.get("kind", "comparison"))
        return bool(query.signature(session, asset["target"], asset["options"]) == asset["stamp"])
    except (ValueError, KeyError):
        return False


def cancel(session: Any, kind: str = "") -> None:
    slots = (kind,) if kind else tuple(session.tissue_inspection.values)
    for key in slots:
        value = session.tissue_inspection.values.pop(key, None)
        if value and value.job:
            session.scheduler.cancel_job(value.job, obsolete=True)


def execute(session: Any, operation: str, arguments: dict[str, Any]) -> Any:
    from .issues import tissue_geometry

    commands: dict[str, Any] = {
        "tissue.inspect.stages": partial(stages.describe, session),
        "tissue.inspect.compare": partial(start, session, "comparison"),
        "tissue.inspect.point": partial(start, session, "point"),
        "tissue.inspect.stacking": partial(start, session, "stacking"),
        "tissue.inspect.status": partial(status, session),
        "tissue.inspect.cancel": partial(cancel, session),
        "tissue.inspect.check": partial(tissue_geometry.request, session),
    }
    if operation not in commands:
        raise ValueError("Unknown tissue inspection operation.")
    return commands[operation](**arguments)
