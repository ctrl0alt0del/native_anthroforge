"""Frozen-revision skin exports use isolated updates and atomic, cancellable serialization."""

import os
import tempfile
from functools import partial
from pathlib import Path
from time import sleep
from typing import Any

from anthroforge.core.jobs import Job
from anthroforge.native.mesh import NativeCancellation

from . import isolated_execution, skin_export_writers, skin_workloads


def export(session: Any, path: str, policy: str, wait: bool = False) -> dict[str, Any]:
    if policy not in ("accepted", "update", "cancel"):
        raise ValueError("Choose accepted, update or cancel for skin export.")
    if policy == "cancel":
        return dict(state="cancelled", path=path)
    session.skin_status.require("export")
    target = export_target(session, path)
    payload = session.document, session.resources.snapshot(), session.preferences.value
    job = make_job(session, target, policy, payload)
    session.scheduler.submit(job)
    if wait:
        wait_for_job(session, job)
    return dict(job=job.id, state=job.state, path=str(target), revision=payload[0].revision)


def export_target(session: Any, path: str) -> Path:
    target = Path(path).expanduser().resolve()
    skin_export_writers.writer(target)
    if any(j.active and "@file:" + str(target) in j.outputs for j in session.scheduler.jobs):
        raise ValueError("Another operation is already writing this file.")
    return target


def make_job(session: Any, path: Path, policy: str, frozen: Any) -> Job:
    job = Job(
        "Export skin",
        frozenset(("@file:" + str(path),)),
        lambda _: frozen,
        partial(write, path, policy),
        lambda _: None,
        writes=False,
        publish_during_edit=True,
        kind="skin_export_update" if policy == "update" else "skin_export",
    )
    job.cancel = NativeCancellation(session.engine)
    job.workload = lambda _: skin_workloads.estimate(frozen[1], frozen[0])
    return job


def wait_for_job(session: Any, job: Job) -> None:
    while job.active:
        session.scheduler.tick()
        sleep(0.005)
    if job.state != "succeeded":
        raise ValueError(job.error or "Skin export " + job.state)


def write(path: Path, policy: str, payload: Any, cancel: Any) -> None:
    document, resources, preferences = payload
    mesh = resources.meshes[document.skin.final.asset].mesh
    if policy == "update":
        mesh = updated(document, resources, preferences, cancel)
    atomic_write(path, mesh, document.revision, cancel)


def updated(document: Any, resources: Any, preferences: Any, cancel: Any) -> Any:
    session = isolated_execution.create(document, resources, preferences, cancel)
    try:
        session.command("evaluate")
        isolated_execution.settle(session, cancel)
        rebuild = session.document.skin.construction_stale
        rebuild |= not session.skin_status.snapshot().operations["update"].available
        session.command("skin.build" if rebuild else "skin.evaluate")
        isolated_execution.settle(session, cancel)
        return completed_mesh(session)
    finally:
        session.close()


def completed_mesh(session: Any) -> Any:
    session.skin_status.require("export")
    if session.document.skin.build_error or session.document.skin.final.status != "ready":
        raise ValueError("Updated skin is incomplete; explicitly export the last accepted skin.")
    return session.assets[session.document.skin.final.asset].mesh


def atomic_write(path: Path, mesh: Any, revision: int, cancel: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(prefix=".anthroforge-skin-", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            skin_export_writers.writer(path)(stream, mesh, revision, cancel)
            stream.flush()
            os.fsync(stream.fileno())
        skin_export_writers.require_running(cancel)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
