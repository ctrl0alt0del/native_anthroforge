"""Pre-edit binding preparation is an ordinary coordinated write job."""

from dataclasses import replace
from functools import partial
from typing import Any

from anthroforge.core.jobs import Job, ObsoleteInputs
from anthroforge.core.results import Port
from anthroforge.core.scheduling import Workload
from anthroforge.native.mesh import NativeCancellation

from . import shortcut_capture, shortcut_contexts


def request(session: Any, key: str) -> str:
    job = Job(
        "Prepare shortcut attachment policy",
        frozenset((key,)),
        partial(prepare, session, key),
        lambda payload, cancel: shortcut_capture.compute(
            session.engine, payload[0], payload[1], cancel
        ),
        partial(publish, session),
        key="shortcut_capture:" + key,
        kind="shortcut_capture",
    )
    configure(session, job, key)
    return str(session.scheduler.submit(job))


def configure(session: Any, job: Job, key: str) -> None:
    job.edit_contexts = (key,)
    job.cancel = NativeCancellation(session.engine)
    job.publish_during_edit = job.restart_on_redo = True
    job.retry = partial(request, session, key)
    job.cleanup = partial(completed, session, key, job)
    job.workload = partial(workload, session, key)
    job.provides = frozenset((Port(key, "shortcut_capture"),))


def prepare(session: Any, key: str, document: Any) -> tuple[Any, Any]:
    context = shortcut_contexts.lookup(document, key)
    if context is None:
        raise ObsoleteInputs("The shortcut edit was superseded before preparation.")
    return context, {k: v.mesh for k, v in session.assets.items()}


def workload(session: Any, key: str, document: Any) -> Workload:
    context = shortcut_contexts.lookup(document, key)
    meshes = [session.assets[v.asset].mesh for v in context.opening if v.asset] if context else []
    return Workload(
        affected=len(context.targets) if context else 0,
        recaptures=len(meshes),
        candidates=sum(m.counts[0] for m in meshes),
        triangles=sum(m.counts[3] for m in meshes),
    )


def publish(session: Any, context: Any) -> None:
    shortcut_contexts.install(session, context)
    from .shortcut_attachment_evaluation import request

    request(session, {context.id})


def completed(session: Any, key: str, job: Job, state: str) -> None:
    context = shortcut_contexts.lookup(session.document, key)
    if state == "failed" and context is not None:
        shortcut_contexts.install(session, replace(context, status="failed", error=job.error))
