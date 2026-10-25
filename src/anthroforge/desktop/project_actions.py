"""Asynchronous file preparation/publication with modal blocked-save semantics."""

from functools import partial
from pathlib import Path

from anthroforge.application import projects, task_workloads
from anthroforge.application.history import History
from anthroforge.application.storage import atomic_save, read_package
from anthroforge.core.jobs import Job

from .controller_actions import local_path, new_document
from .project_view import adopted


def save(controller, path, policy):
    session = controller.session
    if session.history.before is not None:
        session.commit()
    session.scheduler.tick()
    if session.scheduler.blocked and not policy:
        controller.saveChoiceRequested.emit(path)
        return
    if policy == "wait" and session.scheduler.blocked:
        session.waiting_save = True
        controller.pending_save = path
        controller.notify()
        return
    start_save(controller, path, policy)


def start_save(controller, path, policy):
    session = controller.session
    target = Path(local_path(path)).resolve()
    snapshot = (
        session.scheduler.checkpoint
        if policy == "checkpoint" and session.scheduler.blocked
        else session.document
    )
    lock = projects.lock_target(session, target)
    controller.temporary_locks.append(lock)
    session.scheduler.submit(save_job(controller, target, snapshot, lock))


def save_job(controller, target, snapshot, lock):
    session = controller.session
    resources = session.resources.snapshot()
    job = Job(
        "Save project",
        frozenset(("@file:" + str(target),)),
        lambda _: snapshot,
        lambda document, cancel: atomic_save(target, document, resources),
        lambda _: saved(controller, target, lock, snapshot.revision),
        writes=False,
        kind="project_save",
        workload=lambda _: task_workloads.project_save(resources, snapshot),
    )
    job.cleanup = lambda state: cleanup(controller, lock, state)
    return job


def saved(controller, path, lock, revision):
    projects.finish_save(controller.session, path, lock, revision)
    controller.message = f"Saved revision {revision}: {path.name}"
    controller.project_library.remember(path)
    controller.pending_save = ""
    controller.session.waiting_save = False
    controller.notify()
    continue_after_save(controller)


def continue_after_save(controller):
    action, controller.after_save = controller.after_save, None
    if action == "@close":
        controller.closeReady.emit()
    elif action is not None:
        controller.pending_document = action
        controller.session.waiting_save = True


def cleanup(controller, lock, state):
    if lock in controller.temporary_locks:
        controller.temporary_locks.remove(lock)
    if lock is not controller.session.file_lock:
        lock.close()
    if state != "succeeded":
        controller.session.waiting_save = False
        controller.pending_save, controller.after_save = "", None
        controller.message = "File operation did not complete. See Activity for the error."
        controller.notify()


def queue_document(controller, path):
    controller.pending_document = path
    controller.session.waiting_save = True
    for job in controller.session.scheduler.active_jobs:
        if job.active:
            controller.session.scheduler.cancel_job(job.id)


def poll(controller):
    session = controller.session
    if controller.pending_save and not session.scheduler.blocked:
        path, controller.pending_save = controller.pending_save, ""
        start_save(controller, path, "wait")
    if controller.pending_document is not None and not session.scheduler.active_jobs:
        path, controller.pending_document = controller.pending_document, None
        if path:
            start_open(controller, path)
        else:
            new_document(controller)
    controller.project_library.poll()


def start_open(controller, path):
    target = Path(local_path(path)).resolve(strict=True)
    lock = projects.lock_target(controller.session, target)
    controller.temporary_locks.append(lock)
    controller.session.scheduler.submit(open_job(controller, target, lock))


def open_job(controller, target, lock):
    job = Job(
        "Open project",
        frozenset(("@document",)),
        lambda _: target,
        lambda file, cancel: read_package(file, controller.session.engine),
        lambda result: opened(controller, target, lock, result),
        kind="project_open",
        workload=partial(task_workloads.source_file, target),
    )
    job.cleanup = lambda state: cleanup(controller, lock, state)
    return job


def opened(controller, path, lock, result):
    adopt_loaded_state(controller, path, lock, result)
    controller.session.issues.reset()
    projects.synchronize_loaded(controller.session)
    controller.selection, controller.last_revision = "", -1
    controller.refresh()
    adopted(controller)


def adopt_loaded_state(controller, path, lock, result):
    session = controller.session
    session.document, session.resources = result
    session.history = History(session.document)
    session.serial = session.document.revision
    session.active_workspace = 0
    session.waiting_save = False
    controller.project_library.opened(path, lock, session.serial)
