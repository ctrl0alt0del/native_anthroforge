"""Owned, revision-checked assessment of imported SCP source replacement."""

from dataclasses import asdict, dataclass, replace
from functools import partial
from pathlib import Path
from typing import Any
from uuid import uuid4

from anthroforge.core.jobs import Job
from anthroforge.core.results import Port
from anthroforge.core.snapshot_definitions import same
from anthroforge.native import topology
from anthroforge.native.mesh import NativeCancellation

from . import (
    construction_tasks,
    dependencies,
    dependent_tasks,
    entity_revisions,
    mesh_replacement_bindings,
    object_revisions,
    previews,
)
from . import mesh_replacement_policy as policy
from .assets import Asset, imported
from .construction_evaluator import Evaluation
from .construction_policy import revisions
from .evaluation_results import accepted_result
from .geometry_outputs import anatomical_result
from .resources import Resources
from .task_workloads import source_file


@dataclass(frozen=True)
class Candidate:
    entities: dict[str, Any]
    objects: dict[str, Any]
    resources: Resources
    changes: tuple[policy.Change, ...]
    matching: bool
    baseline: dict[str, Any]
    incoming: frozenset[str]


def selected(session: Any, target: str) -> Any:
    item = session.editable(target)
    if item.primitive is None or item.primitive.kind != "IMPORTED":
        raise ValueError("Replace Mesh requires an imported SCP primitive.")
    return item


def assess(
    session: Any, target: str, path: str, units: float | None = None, y_up: bool | None = None
) -> Any:
    if session.history.before is not None or session.waiting_save:
        raise ValueError("Finish the current edit before replacing a source mesh.")
    item = selected(session, target)
    units, y_up = import_settings(session, item, units, y_up)
    source = Path(path).resolve(strict=True)
    return start(session, target, source, units, y_up)


def start(session: Any, target: str, source: Path, units: float, y_up: bool) -> Any:
    previews.cancel(session, "mesh_replacement")
    value = previews.Preview[Candidate](
        str(uuid4()), target, str(session.document.id), state="queued"
    )
    session.mesh_replacement = value
    job = make_job(session, value, source, units, y_up)
    value.job = job.id
    session.scheduler.submit(job)
    return status(session)


def make_job(session: Any, value: Any, source: Path, units: float, y_up: bool) -> Job:
    job = Job(
        "Assess replacement " + source.name,
        frozenset(),
        partial(capture, session, value),
        partial(compute, session, value.target, source, units, y_up),
        partial(publish, session, value),
        key="mesh_replacement",
        kind="mesh_import",
        writes=False,
        publish_during_edit=True,
    )
    return configure_job(session, value, source, job)


def configure_job(session: Any, value: Any, source: Path, job: Job) -> Job:
    job.cancel = NativeCancellation(session.engine)
    job.observes = frozenset(dependencies.graph(session.document))
    job.reads = frozenset(p.owner for p in job.observes)
    job.workload = partial(source_file, source)
    job.cleanup = partial(previews.completed, value, job)
    return job


def capture(session: Any, value: Any, document: Any) -> Any:
    value.ports = set(dependencies.graph(document))
    value.reads, value.state = revisions(document, value.ports), "running"
    return document, session.resources.snapshot()


def compute(
    session: Any, target: str, source: Path, units: float, y_up: bool, payload: Any, cancel: Any
) -> Candidate:
    document, resources = payload
    source_asset = imported(session.engine, source, units, y_up, cancel)
    return replacement(session.engine, target, document, resources, source_asset, cancel)


def replacement(
    engine: Any, target: str, document: Any, resources: Resources, source_asset: Asset, cancel: Any
) -> Candidate:
    before = resources.snapshot()
    original = document.entity(target)
    matching = matches_source(original, resources, source_asset, cancel)
    changes = policy.assess(document, original, matching)
    item, candidate = candidate_geometry(
        engine, document, resources, original, source_asset, changes, cancel
    )
    entities, objects = mesh_replacement_bindings.recapture(
        engine, document, candidate, resources, target, changes, cancel.handle
    )
    entities.setdefault(target, item)
    return bundle(document, target, entities, objects, before, resources, changes, matching)


def bundle(
    document: Any,
    target: str,
    entities: Any,
    objects: Any,
    before: Any,
    resources: Any,
    changes: Any,
    matching: bool,
) -> Candidate:
    baseline = {key: document.object(key) for key in entities.keys() | objects.keys()}
    incoming = frozenset(item.id for item in policy.incoming(document, target))
    return Candidate(
        entities, objects, additions(before, resources), changes, matching, baseline, incoming
    )


def candidate_geometry(
    engine: Any,
    document: Any,
    resources: Any,
    original: Any,
    source: Asset,
    changes: Any,
    cancel: Any,
) -> tuple[Any, Any]:
    source_key, result_key = str(uuid4()), str(uuid4())
    resources.meshes[source_key] = source
    item = policy.adjusted(original, changes)
    item = replace(item, primitive=replace(item.primitive, source=source_key))
    item = entity_revisions.authored(original, item)
    return evaluate_candidate(engine, document, resources, item, result_key, cancel)


def evaluate_candidate(
    engine: Any, document: Any, resources: Any, item: Any, result_key: str, cancel: Any
) -> tuple[Any, Any]:
    meshes = {k: a.mesh for k, a in resources.meshes.items()}
    mesh = Evaluation(engine, document, meshes, cancel, resources.paths).geometry(item)
    resources.meshes[result_key] = Asset(mesh, "generated", "", 1.0, False)
    inputs = dependencies.ports(document, Port(item.id, "geometry"))
    result = accepted_result(document, item, inputs, result_key)
    item = anatomical_result(item, result)
    return item, replace(
        document, entities=tuple(item if e.id == item.id else e for e in document.entities)
    )


def additions(before: Resources, after: Resources) -> Resources:
    return Resources(
        **{
            name: {
                key: value
                for key, value in getattr(after, name).items()
                if key not in getattr(before, name)
            }
            for name in Resources.__dataclass_fields__
        }
    )


def publish(session: Any, value: Any, candidate: Candidate) -> None:
    if session.mesh_replacement is not value or not previews.current(session, value):
        raise ValueError("Replacement inputs changed; assess the mesh again.")
    value.asset, value.state = candidate, "ready"


def status(session: Any) -> dict[str, Any]:
    value = session.mesh_replacement
    state = "stale" if value.state == "ready" and not current(session, value) else value.state
    candidate = value.asset
    return dict(
        token=value.token,
        target=value.target,
        job_id=value.job,
        state=state,
        error=value.error,
        matching_topology=candidate.matching if candidate else None,
        changes=change_rows(session, candidate) if candidate else [],
    )


def apply(session: Any, token: str, approved: list[str] | None = None) -> str:
    value, candidate = require_candidate(session, token, approved or [])
    selected(session, value.target)
    for name in Resources.__dataclass_fields__:
        getattr(session.resources, name).update(getattr(candidate.resources, name))
    install_records(session, candidate)
    construction_tasks.propagate_result(session, value.target)
    target = value.target
    previews.cancel(session, "mesh_replacement")
    return str(target)


def install_records(session: Any, candidate: Candidate) -> None:
    entities = session.authored_entities(candidate.entities)
    objects = {
        key: object_revisions.authored(session.document.object(key), item)
        for key, item in candidate.objects.items()
    }
    ports = changed_object_ports(session, objects)
    session.scheduler.invalidate_ports(ports)
    session.replace_document(
        entities=replaced(session.document.entities, entities),
        objects=replaced(session.document.objects, objects),
    )
    dependent_tasks.changed(session, ports, published=False)


def replaced(records: Any, changes: Any) -> tuple[Any, ...]:
    return tuple(changes.get(item.id, item) for item in records)


def require_candidate(session: Any, token: str, approved: list[str]) -> Any:
    value = session.mesh_replacement
    if (
        token != value.token
        or value.state != "ready"
        or not value.asset
        or not previews.current(session, value)
    ):
        raise ValueError("A current successful mesh replacement assessment is required.")
    require_unchanged(session, value.target, value.asset)
    required = {row.key for row in value.asset.changes}
    if len(set(approved)) != len(approved) or set(approved) != required:
        raise ValueError("Explicitly approve every listed rebind or discarded setting.")
    return value, value.asset


def cancel(session: Any) -> None:
    previews.cancel(session, "mesh_replacement")


def matches_source(original: Any, resources: Any, source: Asset, cancel: Any) -> bool:
    old = resources.meshes[original.primitive.source].mesh
    return topology.same_topology(old, source.mesh, cancel.handle)


def require_unchanged(session: Any, target: str, candidate: Candidate) -> None:
    records = session.document.registry.records
    if any(
        key not in records or not same(before, records[key])
        for key, before in candidate.baseline.items()
    ):
        raise ValueError("Replacement definitions changed; assess again.")
    incoming = frozenset(item.id for item in policy.incoming(session.document, target))
    if incoming != candidate.incoming:
        raise ValueError("Incoming relationships changed; assess again.")


def changed_object_ports(session: Any, objects: dict[str, Any]) -> set[Port]:
    return set().union(
        *(
            object_revisions.changed_ports(session.document.object(key), item)
            for key, item in objects.items()
        )
    )


def import_settings(session: Any, item: Any, units: float | None, y_up: bool | None) -> Any:
    source = session.assets[item.primitive.source]
    return (source.units if units is None else units, source.y_up if y_up is None else y_up)


def current(session: Any, value: Any) -> bool:
    if not previews.current(session, value):
        return False
    try:
        if value.asset:
            require_unchanged(session, value.target, value.asset)
        return True
    except ValueError:
        return False


def change_rows(session: Any, candidate: Candidate) -> list[dict[str, Any]]:
    return [
        dict(asdict(row), name=candidate.baseline[row.target].name) for row in candidate.changes
    ]
