"""Review tissue source changes through owned native evaluation and shared publication."""

from dataclasses import replace
from functools import partial
from typing import Any

from anthroforge.core import tissue_policy
from anthroforge.core.fibers import Fiber
from anthroforge.core.membranes import Membrane
from anthroforge.core.points import Anchor
from anthroforge.core.results import Port
from anthroforge.core.tissue_revisions import PHASES
from anthroforge.core.tissues import TissueVCP

from . import previews, replacement_assessments, replacement_bindings, tissue_tasks
from . import tissue_retarget_evaluation as evaluation
from . import tissue_retarget_policy as policy
from .replacement_reviews import binding_changes, bundle, install_records
from .tissue_operations import tissue

SLOT = "tissue_retarget"


def options(session: Any, target: str) -> list[dict[str, Any]]:
    item = session.document.object(target)
    if not isinstance(item, TissueVCP):
        raise ValueError("Choose a Tissue to inspect its construction choices.")
    return [
        dict(
            id=source.id,
            name=source.name,
            kind=type(source).__name__,
            current=source.id == item.source,
        )
        for source in session.document.objects
        if isinstance(source, (Anchor, Fiber, Membrane))
    ]


def assess(session: Any, target: str, source: str) -> Any:
    if session.history.before is not None or session.waiting_save:
        raise ValueError("Finish the current edit before changing a tissue source.")
    item = tissue(session, target)
    tissue_policy.domain(session.document.object(source))
    if item.source == source:
        return dict(state="unchanged", target=target)
    worker = partial(compute, session, target, source)
    workload = partial(tissue_tasks.workload, session, target, "base")
    return replacement_assessments.start(
        session, SLOT, target, worker, "tissue_source_replace", workload
    )


def compute(session: Any, target: str, source: str, payload: Any, cancel: Any) -> Any:
    document, resources = payload
    before = resources.snapshot()
    original = document.object(target)
    edits = policy.Edits(target)
    item = policy.prepare(original, document.object(source), document.registry.records, edits)
    context = evaluation.Assessment(
        session.engine, document, document, resources, item, edits, cancel.handle
    )
    context.evaluate()
    return completed(context, before)


def completed(context: evaluation.Assessment, before: Any) -> Any:
    target = context.item.id
    matching = evaluation.matching_final(context)
    bindings = [] if matching else binding_changes(context.original, target)
    entities, objects = recaptured(context, bindings)
    objects = {**context.related, **objects, target: context.item}
    changes = tuple((*context.edits.rows, *bindings))
    value = bundle(
        context.original, target, entities, objects, before, context.resources, changes, matching
    )
    return replace(value, prepared=frozenset(Port(target, p) for p in PHASES))


def status(session: Any) -> dict[str, Any]:
    return replacement_assessments.status(session, SLOT)


def apply(session: Any, token: str, approved: list[str] | None = None) -> str:
    value, candidate = replacement_assessments.require(session, SLOT, token, approved or [])
    tissue(session, value.target)
    for name in candidate.resources.__dataclass_fields__:
        getattr(session.resources, name).update(getattr(candidate.resources, name))
    install_records(session, candidate)
    target = value.target
    previews.cancel(session, SLOT)
    return str(target)


def cancel(session: Any) -> None:
    previews.cancel(session, SLOT)


def recaptured(context: evaluation.Assessment, bindings: Any) -> Any:
    return replacement_bindings.recapture(
        context.engine,
        context.original,
        context.document,
        context.resources,
        context.item.id,
        bindings,
        context.cancel,
    )
