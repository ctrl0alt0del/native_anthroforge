"""Explicit region captures are cancellable authored edits with retained material ownership."""

from dataclasses import dataclass, replace
from functools import partial
from typing import Any
from uuid import uuid4

from anthroforge.core import anatomical_surfaces
from anthroforge.core.jobs import Job
from anthroforge.core.results import Port
from anthroforge.core.scheduling import Workload
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.native.mesh import NativeCancellation

from . import authored_jobs, dependencies, object_revisions, surface_providers, tissue_region_goals
from .construction_policy import revisions
from .tissue_operations import tissue


@dataclass(frozen=True)
class Capture:
    target: str
    constraint: str
    reference: SurfaceReference


def selected(item: Any, key: str) -> Any:
    row = next((r for r in item.constraints if r.id == key), None)
    if row is None:
        raise ValueError("Select a tissue region constraint.")
    return row


def bind(session: Any, target: str, constraint: str, parent: str, role: str = "") -> str:
    item = tissue(session, target)
    selected(item, constraint)
    if not item.rest_result.asset:
        raise ValueError("Region capture requires accepted inflated rest geometry.")
    ref = anatomical_surfaces.reference(parent, session.document.registry.records, role)
    surface_providers.get(session.engine, session.document, session.assets, ref)
    spec = Capture(target, constraint, ref)
    return authored_jobs.begin(session, partial(enqueue, session, spec))


def unlink(session: Any, target: str, constraint: str) -> None:
    from .tissue_strategy_operations import install

    item = tissue(session, target)
    row = unbound_region(selected(item, constraint))
    install(
        session,
        replace(
            item, constraints=tuple(row if r.id == constraint else r for r in item.constraints)
        ),
    )


def inputs(document: Any, spec: Capture) -> set[Port]:
    seeds = {Port(spec.target, "rest"), Port(spec.target, "pose")}
    seeds |= surface_providers.ports(document, (spec.reference,))
    return dependencies.closure(dependencies.graph(document), seeds)


def enqueue(session: Any, spec: Capture, origin: int) -> str:
    job = make_job(session, spec, origin)
    job.cancel = NativeCancellation(session.engine)
    job.restart_on_input_change = True
    job.retry = partial(enqueue, session, spec, origin)
    job.observes = job.prerequisites = frozenset(inputs(session.document, spec))
    job.reads = frozenset(p.owner for p in job.observes)
    job.workload = partial(workload, session, spec)
    return str(session.scheduler.submit(job))


def make_job(session: Any, spec: Capture, origin: int) -> Job:
    return Job(
        "Bind tissue region",
        frozenset((spec.target,)),
        lambda document: (document, session.resources.snapshot()),
        partial(compute, session, spec),
        partial(publish, session, spec, origin),
        key="tissue_region:" + spec.target + ":" + spec.constraint,
        kind="tissue_constraint_capture",
    )


def workload(session: Any, spec: Capture, document: Any) -> Workload:
    item = document.object(spec.target)
    asset = session.assets.get(item.rest_result.asset)
    return Workload(affected=1, candidates=asset.mesh.counts[0] if asset else 0, entities=1)


def compute(session: Any, spec: Capture, payload: Any, cancel: Any) -> Any:
    document, resources = payload
    item = document.object(spec.target)
    row = require_capture(item, spec.constraint)
    batch, material, signature = tissue_region_goals.capture(
        session.engine, document, resources, item, spec.reference, cancel.handle
    )
    updated = replace(
        row,
        reference=spec.reference,
        binding_asset=str(uuid4()),
        material_asset=material,
        topology=signature,
    )
    return document, updated, batch


def require_capture(item: Any, constraint: str) -> Any:
    if item.rest_result.status in ("failed", "invalid", "cancelled"):
        raise ValueError("Region capture requires usable inflated rest geometry.")
    return selected(item, constraint)


def publish(session: Any, spec: Capture, origin: int, payload: Any) -> None:
    from . import tissue_tasks

    document, row, batch = payload
    ports = inputs(document, spec)
    if revisions(document, ports) != revisions(session.document, ports):
        raise ValueError("Region capture inputs changed before publication.")
    proof = authored_jobs.Capture(
        revisions(document, ports), partial(enqueue, session, spec, origin)
    )
    authored_jobs.publish(session, origin, partial(merge, spec=spec, row=row), proof)
    session.resources.bindings[row.binding_asset] = batch
    tissue_tasks.edited(session, {Port(spec.target, "intrinsic")})


def merge(document: Any, spec: Capture, row: Any) -> Any:
    item = document.registry.anatomy.get(spec.target)
    if item is None or not any(r.id == row.id for r in item.constraints):
        return document
    values = {
        name: getattr(row, name)
        for name in ("reference", "material_asset", "binding_asset", "topology")
    }
    rows = bound_rows(item, row, values)
    updated = object_revisions.authored(item, replace(item, constraints=rows))
    return replace(
        document, objects=tuple(updated if o.id == item.id else o for o in document.objects)
    )


def bound_rows(item: Any, row: Any, values: Any) -> Any:
    return tuple(
        replace(r, origin="CUSTOM", **values) if r.id == row.id else r for r in item.constraints
    )


def unbound_region(row: Any) -> Any:
    return replace(
        row, origin="CUSTOM", reference=None, material_asset="", binding_asset="", topology=""
    )
