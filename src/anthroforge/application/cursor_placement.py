"""Confirmed cursor placement updates presentation only, with cancellable owned queries."""

from functools import partial
from typing import Any, cast

from anthroforge.core.jobs import Job, ObsoleteInputs
from anthroforge.native.mesh import NativeCancellation

from . import presentation, snap_edits, surface_providers
from .construction_policy import revisions


def request(session: Any, origin: Any, direction: Any, targets: Any) -> str:
    from .snap_tasks import validate_request

    validate_request(True, targets, origin, direction, 0)
    data = dict(origin=tuple(origin), direction=tuple(direction), targets=tuple(targets), offset=0)
    workspace = workspace_key(session)
    job = make_job(session, data, workspace)
    job.cancel = NativeCancellation(session.engine)
    job.observes = job.prerequisites = frozenset(surface_providers.ports(session.document, targets))
    return cast(str, session.scheduler.submit(job))


def make_job(session: Any, data: Any, workspace: Any) -> Job:
    return Job(
        "Place cursor on exterior surface",
        frozenset(("workspace:" + str(workspace[0]),)),
        lambda doc: snap_edits.Context(session.engine, doc, session.resources.snapshot()),
        partial(compute, data),
        partial(publish, session, data, workspace),
        key="cursor_placement",
        kind="surface_snap",
    )


def compute(data: Any, context: Any, cancel: Any) -> Any:
    return context.document, snap_edits.destination(context, data, cancel.handle)


def publish(session: Any, data: Any, workspace: Any, result: Any) -> None:
    document, point = result
    ports = surface_providers.ports(document, data["targets"])
    if revisions(document, ports) != revisions(session.document, ports):
        raise ObsoleteInputs()
    if workspace_key(session) != workspace:
        raise ObsoleteInputs()
    presentation.update_workspace(session, cursor=point)


def workspace_key(session: Any) -> Any:
    current = session.workspace
    return session.active_workspace, current.name, current.members, current.focused, current.cursor
