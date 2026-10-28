"""Owned, revision-checked assessment of imported SCP source replacement."""

from dataclasses import replace
from functools import partial
from pathlib import Path
from typing import Any
from uuid import uuid4

from anthroforge.core.results import Port
from anthroforge.native import topology

from . import (
    construction_tasks,
    dependencies,
    entity_revisions,
    previews,
    replacement_assessments,
    replacement_bindings,
    replacement_status,
)
from . import mesh_replacement_policy as policy
from .assets import Asset, imported
from .construction_evaluator import Evaluation
from .evaluation_results import accepted_result
from .geometry_outputs import anatomical_result
from .replacement_reviews import (
    Candidate,
    bundle,
    install_records,
)
from .resources import Resources
from .task_workloads import source_file


def selected(session: Any, target: str) -> Any:
    item = session.editable(target)
    if item.primitive is None or item.primitive.kind != "IMPORTED":
        raise ValueError("Replace Mesh requires an imported SCP primitive.")
    return item


def assess(
    session: Any, target: str, path: str, units: float | None = None, y_up: bool | None = None
) -> Any:
    replacement_status.assess(session, "mesh_replacement", target).require()
    item = selected(session, target)
    units, y_up = import_settings(session, item, units, y_up)
    source = Path(path).resolve(strict=True)
    return start(session, target, source, units, y_up)


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
    entities, objects = replacement_bindings.recapture(
        engine, document, candidate, resources, target, changes, cancel.handle
    )
    entities.setdefault(target, item)
    return bundle(document, target, entities, objects, before, resources, changes, matching)


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


def cancel(session: Any) -> None:
    previews.cancel(session, "mesh_replacement")


def matches_source(original: Any, resources: Any, source: Asset, cancel: Any) -> bool:
    old = resources.meshes[original.primitive.source].mesh
    return topology.same_topology(old, source.mesh, cancel.handle)


def import_settings(session: Any, item: Any, units: float | None, y_up: bool | None) -> Any:
    source = session.assets[item.primitive.source]
    return (source.units if units is None else units, source.y_up if y_up is None else y_up)


def start(session: Any, target: str, source: Path, units: float, y_up: bool) -> Any:
    worker = partial(compute, session, target, source, units, y_up)
    replacement_assessments.start(
        session, "mesh_replacement", target, worker, "mesh_import", partial(source_file, source)
    )
    return status(session)


def status(session: Any) -> dict[str, Any]:
    result = replacement_assessments.status(session, "mesh_replacement")
    result["matching_topology"] = result.pop("matching_correspondence")
    return result


def require_candidate(session: Any, token: str, approved: list[str]) -> Any:
    return replacement_assessments.require(session, "mesh_replacement", token, approved)
