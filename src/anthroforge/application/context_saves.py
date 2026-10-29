"""One project save captures committed context states without persisting active jobs."""

from dataclasses import replace
from typing import Any, cast

from anthroforge.core.document import Document
from anthroforge.core.reconstruction import SceneSnapshot

from .editing_contexts import bare
from .scheduling_context import all_active


def scene(session: Any, key: str, checkpoints: bool) -> Document:
    context = session.contexts.states[key]
    current = context.values["document"]
    before = context.values["history"].before
    scheduling = session.scheduler.scheduling_contexts[key]
    if checkpoints and any(j.writes for j in scheduling.registry.active.values()):
        current = scheduling.checkpoint
    if before is not None and before.revision < current.revision:
        current = before
    return cast(Document, current)


def project(session: Any, checkpoints: bool = False) -> Document:
    contexts = {key: scene(session, key, checkpoints) for key in session.contexts.states}
    accepted = contexts[""]
    state = accepted.reconstruction
    snapshots = {row.id: row for row in state.snapshots}
    for variant in state.variants:
        if variant.id in contexts:
            snapshots[variant.current] = SceneSnapshot(bare(contexts[variant.id]), variant.current)
    historical = historical_revisions(session, contexts)
    return replace(
        accepted,
        reconstruction=replace(state, snapshots=tuple(snapshots.values())),
        revision=min(historical, default=session.serial),
    )


def historical_revisions(session: Any, contexts: Any) -> list[int]:
    return [row.revision for key, row in contexts.items() if row is not session.contexts.scene(key)]


def pending(session: Any) -> list[str]:
    return [job.id for job in all_active(session.scheduler) if job.writes]


def require_committed(session: Any) -> None:
    if any(
        state.values["history"].before is not None for state in session.contexts.states.values()
    ):
        raise ValueError("Commit or cancel the active edit before saving.")
