"""Application-owned strokes shared by desktop, Python and JSON clients."""

from copy import deepcopy
from dataclasses import replace
from math import isfinite
from typing import Any

from anthroforge.core.painting import Provenance, StrokeInput, SurfaceReference, brush, samples

from . import painting_consumers as consumers
from .painting_state import Stroke, get, require_current


def begin(session: Any, consumer: str, target: str, **options: Any) -> dict[str, Any]:
    require_idle(session)
    value = create(session, consumer, target, options, True)
    session.painting.active = value.token
    return status(session, value.token)


def require_idle(session: Any) -> None:
    if session.painting.active:
        raise ValueError("Finish the current stroke before starting another.")
    if session.history.before is not None or session.waiting_save:
        raise ValueError("Finish the current edit or save before painting.")


def create(session: Any, kind: str, target: str, options: Any, interactive: bool) -> Stroke:
    definition = consumers.consumer(kind)
    definition.require(session, target)
    options, inputs = decode(options)
    definition.validate(session, target, options)
    value = make_stroke(session, kind, target, options, inputs, interactive)
    previous = session.painting.values.get(consumers.name(kind))
    if previous:
        cancel(session, previous.token)
    session.painting.values[value.consumer] = value
    return value


def make_stroke(
    session: Any, kind: str, target: str, options: Any, inputs: Any, interactive: bool
) -> Stroke:
    return Stroke(
        consumers.name(kind),
        target,
        inputs,
        options,
        consumers.consumer(kind).signature(session, target, options),
        provenance(session, kind, target, options),
        interactive=interactive,
    )


def decode(options: Any) -> tuple[dict[str, Any], StrokeInput]:
    values = deepcopy(options)
    config = brush(values.pop("brush", None))
    points = samples(values.pop("samples", ()))
    view = tuple(float(v) for v in values.get("view", ()))
    if len(view) != 14 or any(not isfinite(v) for v in view):
        raise ValueError("Paint requires the existing 14-value finite camera definition.")
    values.update(view=view, stage=values.get("stage", "final"))
    return values, StrokeInput(config, view, points)


def provenance(session: Any, kind: str, target: str, options: Any) -> Provenance:
    asset, frame = consumers.consumer(kind).surface(session, target, options)
    surface = SurfaceReference(target, options["stage"], asset, session._editing.key, tuple(frame))
    return Provenance(str(session.document.id), session.document.revision, surface)


def append(session: Any, token: str, samples: Any) -> dict[str, Any]:
    from anthroforge.core.painting import samples as decode_samples

    from .painting_jobs import request

    value = get(session, token)
    require_drawing(session, value)
    require_current(session, value)
    points = decode_samples((*value.inputs.samples, *decode_samples(samples)))
    value.inputs = replace(value.inputs, samples=points)
    value.sequence += 1
    if points:
        request(session, value)
    return status(session, token)


def require_drawing(session: Any, value: Stroke) -> None:
    if session.painting.active != value.token or value.finishing:
        raise ValueError("This stroke no longer accepts samples.")
    if value.state not in ("drawing", "queued", "running", "ready"):
        raise ValueError("This stroke failed or was cancelled.")


def finish(session: Any, token: str) -> dict[str, Any]:
    from .painting_jobs import request

    value = get(session, token)
    if session.painting.active != token or value.finishing:
        raise ValueError("This stroke has already finished or was cancelled.")
    if not value.inputs.samples:
        raise ValueError("Place at least one paint sample before finishing.")
    require_current(session, value)
    value.finishing = True
    request(session, value)
    return status(session, token)


def preview(session: Any, consumer: str, target: str, **options: Any) -> dict[str, Any]:
    from .painting_jobs import request

    if session.painting.active:
        raise ValueError("Finish the current interactive stroke before requesting another preview.")
    value = create(session, consumer, target, options, False)
    if not value.inputs.samples:
        cancel(session, value.token)
        raise ValueError("A preview needs at least one paint sample.")
    request(session, value)
    return status(session, value.token)


def status(session: Any, token: str) -> dict[str, Any]:
    from .painting_queries import describe_stroke

    return describe_stroke(session, get(session, token))


def result(
    session: Any, token: str, offset: int = 0, limit: int = 4096, expected_revision: str = ""
) -> dict[str, Any]:
    from .painting_queries import result as read

    return read(session, get(session, token), offset, limit, expected_revision)


def cancel(session: Any, token: str = "") -> None:
    values = (get(session, token),) if token else tuple(session.painting.values.values())
    for value in values:
        if value.job and value.job in session.scheduler.registry.by_id:
            session.scheduler.cancel_job(value.job, obsolete=True, reason="painting_cancelled")
        value.asset, value.stamp, value.state, value.finishing = None, None, "cancelled", False
        value.inputs = replace(value.inputs, samples=())
        if session.painting.active == value.token:
            session.painting.active = ""


def apply(session: Any, token: str) -> None:
    value = get(session, token)
    if not value.asset or value.candidate_sequence != value.sequence or value.state != "ready":
        raise ValueError("The stroke is incomplete, cancelled or already committed.")
    require_current(session, value)
    definition = consumers.consumer(value.consumer)
    definition.require(session, value.target)
    definition.apply(session, value)
    value.state, value.finishing = "committed", False
    if session.painting.active == token:
        session.painting.active = ""
