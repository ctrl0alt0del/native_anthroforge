"""Explicit, bounded tissue checks; contact and permitted crossings never block publication."""

from typing import Any
from dataclasses import asdict

from anthroforge.core.issues import Issue, evidence, fingerprint
from anthroforge.core.results import geometry_asset
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import inspection as native, scene
from anthroforge.native.mesh import NativeCancellation

from .. import tissue_inspection_stages as stages
from ..inspection_context import freeze
from ..object_frames import Frames
from .providers import Provider

NAME = "tissue_geometry.v1"
LIMIT = 512
LIMITATIONS = "Transverse triangle crossings and degenerate faces only. Touching/coplanar contact is excluded; containment and penetration depth are not measured."


def scopes(document: Any) -> set[str]:
    return {o.id + ":" + s for o in document.objects if isinstance(o, TissueVCP)
            for s in stages.STAGES if stages.result(o, s).asset and (s != "base" or o.base_state.kind == "SURFACE")}


def provider(session: Any) -> Provider:
    return Provider(NAME, scopes, affected, source, check, lambda _: freeze(session),
                    lambda: NativeCancellation(session.engine), automatic=False)


def affected(document: Any, changes: Any) -> set[str]:
    rows = (*changes.entities.values(), *changes.objects.values())
    fields = {"@membership", "result", "matrix", "geometry_offset", "base_result", "rest_result", "intrinsic_result", "final_result"}
    return scopes(document) if any(fields & row for row in rows) else set()


def neighbors(document: Any, target: str) -> list[Any]:
    return [item for item in document.registry.anatomy.values()
            if item.id != target and geometry_asset(item)]


def source(document: Any, scope: str) -> Any:
    target, stage = scope.rsplit(":", 1)
    item = document.registry.records.get(target)
    if not isinstance(item, TissueVCP):
        return None
    return (str(document.id), asdict(stages.result(item, stage)), item.matrix,
            tuple((o.id, o.matrix, getattr(o, "parent", ""), getattr(o, "follow", "")) for o in document.registry.records.values()),
            tuple((o.id, asdict(o.result), o.matrix, getattr(o, "geometry_offset", ())) for o in neighbors(document, target)))


def request(session: Any, target: str, stage: str = "final") -> dict[str, Any]:
    stages.mesh(session, target, stage)
    scope = target + ":" + stage
    session.issues.listening.invalidate(NAME, {scope})
    session.issues.listening.synchronize()
    job = session.issues.listening.running.get(NAME)
    return dict(scope=scope, job=job.id if job else "", state="queued")


def check(context: Any, scope: str, cancel: Any) -> tuple[Issue, ...]:
    target, stage = scope.rsplit(":", 1)
    item, mesh = stages.tissue(context, target), stages.mesh(context, target, stage)
    others = neighbors(context.document, target)
    frames = Frames(context.engine, context.document)
    resources = [context.resources.meshes[geometry_asset(o)].mesh for o in others]
    ids, bounds, truncated = native.findings(mesh, stages.frame(context, item, stage), resources,
                                           [scene.geometry_matrix(context.engine, frames.world(o.id), getattr(o, "geometry_offset", (0, 0, 0))) for o in others], LIMIT, cancel.handle)
    stamp = fingerprint(source(context.document, scope))
    rows = tuple(finding(context, scope, stamp, item, stage, others, row, box, i)
                 for i, (row, box) in enumerate(zip(ids, bounds, strict=True)))
    return rows + ((limit_issue(scope, target, stage, stamp),) if truncated else ())


def finding(context: Any, scope: str, stamp: str, item: Any, stage: str, others: Any, row: Any, box: Any, index: int) -> Issue:
    code = {1: "DEGENERATE_FACE", 2: "SELF_CROSSING", 3: "SURFACE_CROSSING"}[row[0]]
    other = others[row[1]] if row[1] >= 0 else None
    witness = dict(asset=stages.result(item, stage).asset, triangle=row[2], bounds=box,
                   frame=stages.frame(context, item, stage), other=other.id if other else item.id,
                   other_asset=geometry_asset(other) if other else stages.result(item, stage).asset,
                   other_triangle=row[3], revision=context.document.revision)
    return Issue(NAME, scope, code, code.replace("_", " ").capitalize(), target=item.id,
                 kind="TISSUE", stage=stage, severity="warning", source=stamp, local_key=str(index),
                 related=(other.id,) if other else (), details=LIMITATIONS + " Tissue self-intersections are allowed; this is advisory.",
                 evidence=evidence(witness=witness))


def limit_issue(scope: str, target: str, stage: str, stamp: str) -> Issue:
    return Issue(NAME, scope, "FINDING_LIMIT", "Geometry finding limit reached", target=target,
                 kind="TISSUE", stage=stage, source=stamp, details="Stopped after 512 findings. Unvisited geometry is not certified clean.")
