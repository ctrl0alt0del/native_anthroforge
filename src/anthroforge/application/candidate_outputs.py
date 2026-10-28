"""Candidate publication adapters over the production numerical evaluators."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core.entities import SCP
from anthroforge.core.results import ControlResult, Port
from anthroforge.core.tissues import TissueVCP

from . import (
    construction_tasks,
    curve_evaluation,
    dependencies,
    evaluation,
    geometry_outputs,
    point_evaluation,
    surface_results,
    tissue_evaluation,
    tissue_results,
)
from .assets import Asset
from .construction_policy import revisions
from .evaluation_results import accepted_result
from .object_frames import Frames


def geometry(context: Any, port: Port) -> None:
    item = context.document.object(port.owner)
    if isinstance(item, SCP) and item.primitive is None:
        return
    mesh = construction_tasks.compute_geometry(
        context, context.document, context.resources, port.owner, context.cancel
    )
    key = str(uuid4())
    context.assets[key] = Asset(mesh, "replacement candidate", "", 1.0, False)
    result = accepted(context, item, port, key)
    updated = mesh_publication(item)
    context.install(updated(item, result))


def path(context: Any, port: Port) -> None:
    output = compute_path(context, port)
    item = curve_evaluation.adopt(context, context.document.object(port.owner), output)
    key = str(uuid4())
    context.resources.paths[key] = output.asset
    context.install(replace(item, result=accepted(context, item, port, key)))


def compute_path(context: Any, port: Port) -> Any:
    prefs = context.preferences
    return curve_evaluation.evaluate(
        context.engine,
        context.document,
        context.resources,
        port.owner,
        context.cancel.handle,
        prefs.routing_backend,
        prefs.fiber_propagation,
    )


def accepted(context: Any, item: Any, port: Port, key: str) -> Any:
    return accepted_result(context.document, item, dependencies.ports(context.document, port), key)


def mesh_publication(item: Any) -> Any:
    return geometry_outputs.anatomical_result if isinstance(item, SCP) else surface_results.accepted


def anchor(context: Any, port: Port) -> None:
    from .anchor_tasks import adopt

    item = context.document.object(port.owner)
    resolved = point_evaluation.resolve(
        context.engine, context.document, context.assets, item, context.cancel.handle
    )
    result = accepted_result(context.document, item, dependencies.ports(context.document, port), "")
    context.install(adopt(item, resolved, result))


def control(context: Any, port: Port) -> None:
    item = context.document.control(port.owner)
    frame = Frames(context.engine, context.document).world(item.id)
    reads = revisions(context.document, dependencies.ports(context.document, port))
    context.install(replace(item, result=ControlResult(frame, reads, item.result.revision + 1)))


def pose(context: Any, port: Port) -> None:
    if port.owner in context.fixed_poses or not context.document.attachments_enabled:
        return
    item = context.document.entity(port.owner)
    meshes = {key: asset.mesh for key, asset in context.assets.items()}
    _, result = evaluation.compute(
        context.engine, (context.document, meshes), {item.id}, set(), context.cancel
    )
    updated = next(row for row in result if row.id == item.id)
    if updated.status == "failed":
        raise ValueError(updated.error)
    revision = item.pose_revision + int(
        (item.matrix, item.geometry_offset) != (updated.matrix, updated.geometry_offset)
    )
    context.install(replace(updated, pose_revision=revision))


def tissue(context: Any, port: Port) -> None:
    from .candidate_tissues import grouped

    if grouped(context, port):
        return
    publish_tissue(context, port, compute_tissue(context, port))


def compute_tissue(context: Any, port: Port) -> Any:
    return tissue_evaluation.evaluate(
        context.engine,
        context.document,
        context.resources,
        port.owner,
        port.output,
        context.cancel.handle,
    )


def publish_tissue(context: Any, port: Port, output: Any) -> None:
    item = context.document.object(port.owner)
    key = tissue_results.register(context, output, port.output)
    reads = dependencies.ports(context.document, port)
    result = tissue_results.accept(context.document, item, port.output, reads, key, output)
    context.install(replace(item, **tissue_results.publication(item, port.output, result, output)))


def failure(context: Any, port: Port, message: str) -> None:
    item = context.document.object(port.owner)
    if isinstance(item, TissueVCP):
        context.install(tissue_results.failed(item, port.output, message))
    elif isinstance(item, SCP) and port.output == "pose":
        context.install(replace(item, status="failed", error=message))
    elif hasattr(item, "result"):
        context.install(replace(item, result=replace(item.result, status="failed", error=message)))


def handler(document: Any, port: Port) -> Any:
    if port.output == "formula":
        from .candidate_formulas import handler as formula

        return formula
    if port.owner not in document.registry.records:
        return None
    if isinstance(document.object(port.owner), TissueVCP):
        return tissue if port.output in ("base", "rest", "intrinsic", "plan", "final") else None
    if port.output == "pose":
        return pose if isinstance(document.object(port.owner), SCP) else None
    families = dict(geometry=geometry, path=path, binding=anchor, control=control)
    families.update({name: tissue for name in ("base", "rest", "intrinsic", "plan", "final")})
    return families.get(port.output)
