"""Read-only native presentation jobs with complete staged mesh/picking publication."""

from functools import partial

import numpy as np

from anthroforge.application.curve_sources import world
from anthroforge.core.entities import IDENTITY
from anthroforge.core.fiber_presentation import settings
from anthroforge.core.jobs import Job, ObsoleteInputs
from anthroforge.core.results import Port
from anthroforge.core.scheduling import Workload
from anthroforge.native import path_display, scene
from anthroforge.native.mesh import NativeCancellation

from . import mirror_scene
from .models import RenderModel


class FiberDisplay:
    def __init__(self, controller):
        self.controller = controller
        self.model = RenderModel(controller)
        self.desired, self.accepted, self.jobs = {}, {}, {}
        self.context = None
        self.model.activated.connect(controller.activate_geometry)

    def synchronize(self, records):
        session = self.controller.session
        context = (id(session), session.document.id)
        if context != self.context:
            self.clear()
            self.context = context
        self.desired = {row["id"]: row for row in records if row.get("fiber_radius", 0) > 0}
        for key in self.accepted.keys() - self.desired.keys():
            self.accepted.pop(key)
        self.cancel_missing(session)
        for row in self.desired.values():
            self.request(row)
        self.publish_rows()

    def cancel_missing(self, session):
        for key, job in tuple(self.jobs.items()):
            if key not in self.desired:
                session.scheduler.cancel_job(job[0])
                self.jobs.pop(key, None)

    def clear(self):
        self.desired = {}
        for job, _ in tuple(self.jobs.values()):
            self.controller.session.scheduler.cancel_job(job)
        self.jobs, self.accepted, self.desired = {}, {}, {}
        self.model.publish([])

    def request(self, row):
        session, key = self.controller.session, row["id"]
        token = (session.document.id, signature(row))
        if self.accepted.get(key, (None,))[0] == token:
            return
        if not self.ready_request(key, token):
            return
        job = create_job(self, row, token)
        job.cancel = NativeCancellation(session.engine)
        job.observes = frozenset((Port(key, "path"), Port(key, "pose")))
        job.reads = frozenset((key,))
        job.workload = partial(workload, session, row["asset"])
        job.cleanup = partial(completed, self, key, job.id)
        self.jobs[key] = (session.scheduler.submit(job), token)

    def ready_request(self, key, token):
        existing = self.jobs.get(key)
        if not existing:
            return True
        job = self.controller.session.scheduler.registry.by_id[existing[0]]
        if not job.active:
            return True
        if existing[1] == token:
            return False
        self.jobs.pop(key)
        self.controller.session.scheduler.cancel_job(job.id, obsolete=True)
        return True

    def adopt(self, row, token, mesh):
        current = self.desired.get(row["id"])
        if current is None or current_token(self.controller.session, row["id"]) != token:
            raise ObsoleteInputs()
        self.accepted[row["id"]] = (token, mesh)
        self.publish_rows()

    def publish_rows(self):
        rows, resources = [], []
        for key, row in self.desired.items():
            if key not in self.accepted:
                continue
            token, mesh = self.accepted[key]
            rows.extend(display_rows(row, token, mesh))
            resources.append(mesh)
        self.model.publish(mirror_scene.fiber_rows(self.controller, rows), resources)

    def hits(self, origin, direction):
        rows = [row for row in self.model.active_rows() if row["visible"] and row["pickable"]]
        if not rows:
            return []
        result = scene.pick(
            self.controller.session.engine,
            np.array([row["handle"] for row in rows], dtype=np.uint64),
            np.ascontiguousarray([row["matrix"] for row in rows]),
            origin,
            direction,
        )
        return [surface_hit(rows[int(hit[0])]["id"], hit) for hit in result]

    def memory_owners(self, owners):
        owners["cache"].update(mesh for _, mesh in self.accepted.values())


def signature(row):
    return row["asset"], tuple(row["matrix"]), row["fiber_radius"]


def current_token(session, key, document=None):
    document = document or session.document
    item = document.registry.construction.get(key)
    if item is None:
        return None
    return document.id, (
        item.result.asset,
        world(session.engine, document, key),
        settings(document.workspaces[session.active_workspace], key).radius,
    )


def create_job(display, row, token):
    return Job(
        "Display " + row["name"],
        frozenset(),
        partial(capture, display, row, token),
        partial(compute, row["fiber_radius"]),
        partial(display.adopt, row, token),
        key="fiber-display:" + row["id"],
        kind="fiber_display",
        writes=False,
    )


def compute(radius, payload, cancel):
    if payload is None:
        raise ObsoleteInputs()
    path, frame = payload
    return path_display.tube(path, frame, radius, cancel=cancel.handle)


def capture(display, row, token, document):
    session = display.controller.session
    if current_token(session, row["id"], document) != token:
        return None
    asset = session.resources.paths.get(row["asset"])
    return (asset.path, tuple(row["matrix"])) if asset else None


def workload(session, asset, _):
    return Workload(candidates=session.resources.paths[asset].path.count)


def completed(display, key, job_id, state):
    if display.jobs.get(key, (None,))[0] != job_id:
        return
    display.jobs.pop(key)


def display_rows(row, token, mesh):
    content = dict(source=token[1][0], radius=token[1][2])
    return [
        dict(
            row,
            handle=mesh.handle,
            matrix=IDENTITY,
            geometry_asset=token[1][0],
            key=f"{row['id']}:{mesh.handle}:{chunk}",
            chunk=chunk,
            content=content,
        )
        for chunk in range(mesh.counts[4])
    ]


def surface_hit(key, row):
    return dict(id=key, distance=row[1], face=-1, triangle=-1, vertex=-1, point=row[5:8])
