"""Explicit, bounded tissue checks; contact and permitted crossings never block publication."""

from typing import Any

from anthroforge.core.issues import Issue, evidence, fingerprint
from anthroforge.core.results import geometry_asset
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import inspection as native
from anthroforge.native import scene
from anthroforge.native.mesh import NativeCancellation

from .. import tissue_inspection_stages as stages
from ..inspection_context import freeze
from ..object_frames import Frames
from .providers import Provider

NAME = "tissue_geometry.v1"
LIMIT = 512
LIMITATIONS = (
    "Transverse triangle crossings and degenerate faces only. "
    "Touching/coplanar contact is excluded; containment and penetration depth are not measured."
)
GEOMETRY_FIELDS = frozenset(
    (
        "@membership",
        "result",
        "matrix",
        "geometry_offset",
        "pose_result",
        "parent",
        "follow",
        "base_result",
        "rest_result",
        "intrinsic_result",
        "final_result",
    )
)


def scopes(document: Any) -> set[str]:
    return {
        o.id + ":" + s
        for o in document.objects
        if isinstance(o, TissueVCP)
        for s in stages.STAGES
        if stages.result(o, s).asset and (s != "base" or o.base_state.kind == "SURFACE")
    }


def provider(session: Any) -> Provider:
    return Provider(
        NAME,
        scopes,
        affected,
        source,
        check,
        lambda _: freeze(session),
        lambda: NativeCancellation(session.engine),
        automatic=False,
    )


def affected(document: Any, changes: Any) -> set[str]:
    rows = (*changes.entities.values(), *changes.objects.values())
    return scopes(document) if any(GEOMETRY_FIELDS & row for row in rows) else set()


def neighbors(document: Any, target: str) -> list[Any]:
    return [
        item
        for item in document.registry.anatomy.values()
        if item.id != target and geometry_asset(item)
    ]


def source(document: Any, scope: str) -> Any:
    target, stage = scope.rsplit(":", 1)
    item = document.registry.records.get(target)
    if not isinstance(item, TissueVCP):
        return None
    return (
        str(document.id),
        stages.result(item, stage).asset,
        item.matrix,
        poses(document),
        tuple(
            (o.id, geometry_asset(o), getattr(o, "geometry_offset", ()))
            for o in neighbors(document, target)
        ),
    )


def poses(document: Any) -> tuple[Any, ...]:
    return tuple(
        (
            o.id,
            o.matrix,
            getattr(o, "parent", ""),
            getattr(o, "follow", ""),
            getattr(getattr(o, "pose_result", None), "matrix", ()),
        )
        for o in document.registry.records.values()
    )


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
    resources = [context.resources.meshes[geometry_asset(o)].mesh for o in others]
    scan = native.findings(
        mesh,
        stages.frame(context, item, stage),
        resources,
        [neighbor_frame(context, o) for o in others],
        LIMIT,
        cancel.handle,
    )
    return findings(context, scope, item, stage, others, scan)


def neighbor_frame(context: Any, item: Any) -> Any:
    frame = Frames(context.engine, context.document).world(item.id)
    return tuple(
        scene.geometry_matrix(context.engine, frame, getattr(item, "geometry_offset", (0, 0, 0)))
    )


def findings(
    context: Any, scope: str, item: Any, stage: str, others: Any, scan: Any
) -> tuple[Issue, ...]:
    ids, bounds, truncated = scan
    stamp = fingerprint(source(context.document, scope))
    rows = tuple(
        finding(context, scope, stamp, item, stage, others, row, box, i)
        for i, (row, box) in enumerate(zip(ids, bounds, strict=True))
    )
    return rows + ((limit_issue(scope, item.id, stage, stamp),) if truncated else ())


def finding(
    context: Any,
    scope: str,
    stamp: str,
    item: Any,
    stage: str,
    others: Any,
    row: Any,
    box: Any,
    index: int,
) -> Issue:
    code = {1: "DEGENERATE_FACE", 2: "SELF_CROSSING", 3: "SURFACE_CROSSING"}[row[0]]
    other = others[row[1]] if row[1] >= 0 else None
    sample = witness(context, item, stage, other, row, box)
    return make_issue(scope, stamp, item, stage, other, code, index, sample)


def witness(context: Any, item: Any, stage: str, other: Any, row: Any, box: Any) -> Any:
    result = stages.result(item, stage)
    return dict(
        asset=stages.result(item, stage).asset,
        triangle=row[2],
        bounds=box,
        frame=stages.frame(context, item, stage),
        other=other.id if other else item.id,
        other_asset=geometry_asset(other) if other else stages.result(item, stage).asset,
        other_triangle=row[3],
        other_frame=neighbor_frame(context, other) if other else stages.frame(context, item, stage),
        accepted_revision=result.revision,
        revision=context.document.revision,
    )


def make_issue(
    scope: str, stamp: str, item: Any, stage: str, other: Any, code: str, index: int, sample: Any
) -> Issue:
    fields = issue_fields(item, stage, other, index)
    return Issue(
        NAME,
        scope,
        code,
        code.replace("_", " ").capitalize(),
        source=stamp,
        evidence=evidence(witness=sample),
        **fields,
    )


def issue_fields(item: Any, stage: str, other: Any, index: int) -> dict[str, Any]:
    return dict(
        target=item.id,
        kind="TISSUE",
        stage=stage,
        severity="warning",
        local_key=str(index),
        related=(other.id,) if other else (),
        details=LIMITATIONS + " Tissue self-intersections are allowed; this is advisory.",
    )


def limit_issue(scope: str, target: str, stage: str, stamp: str) -> Issue:
    return Issue(
        NAME,
        scope,
        "FINDING_LIMIT",
        "Geometry finding limit reached",
        target=target,
        kind="TISSUE",
        stage=stage,
        source=stamp,
        details="Stopped after 512 findings. Unvisited geometry is not certified clean.",
    )
