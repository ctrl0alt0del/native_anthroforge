"""On-demand SCP, construction and skin surface checks share qualified native predicates."""

from typing import Any

from anthroforge.core.issues import Issue, evidence, fingerprint
from anthroforge.core.mirroring import source as original
from anthroforge.core.results import geometry_asset
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import inspection
from anthroforge.native.mesh import NativeCancellation

from .. import inspection_surfaces, spatial_evidence
from ..inspection_context import freeze
from . import tissue_geometry
from .providers import Provider

NAME = "surface_geometry.v1"
LIMIT = 512


def scopes(document: Any) -> set[str]:
    objects = inspection_surfaces.targets(document)
    rows = {
        key + ":geometry"
        for key in objects
        if not isinstance(document.object(original(key)), TissueVCP)
    }
    rows.update(
        inspection_surfaces.skin_id(document) + ":" + stage
        for stage in ("envelope", "topology", "final")
        if getattr(document.skin, stage).asset
    )
    return rows


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
    rows = (*changes.entities.values(), *changes.controls.values(), *changes.objects.values())
    relevant = {"skin", "mirror_rules"} & changes.document
    return (
        scopes(document)
        if relevant or any(tissue_geometry.GEOMETRY_FIELDS & row for row in rows)
        else set()
    )


def source(document: Any, scope: str) -> Any:
    target, stage = scope.rsplit(":", 1)
    asset = source_asset(document, target, stage)
    return (
        str(document.id),
        target,
        stage,
        asset,
        tissue_geometry.poses(document),
        tissue_geometry.neighbor_revisions(document, target),
        repr(document.mirrors.signature),
    )


def source_asset(document: Any, target: str, stage: str) -> str:
    return (
        getattr(document.skin, stage).asset
        if target == inspection_surfaces.skin_id(document)
        else geometry_asset(document.object(original(target)))
    )


def request(session: Any, target: str, stage: str = "final") -> dict[str, Any]:
    surface = inspection_surfaces.get(session, target, stage)
    surface.mesh(session)
    if surface.kind == "TISSUE":
        return tissue_geometry.request(session, target, stage)
    scope = surface.target + ":" + surface.stage
    session.issues.listening.invalidate(NAME, {scope})
    session.issues.listening.synchronize()
    job = session.issues.listening.running.get(NAME)
    return dict(scope=scope, job=job.id if job else "", state="queued")


def neighbors(context: Any, target: str) -> list[Any]:
    return [
        inspection_surfaces.get(context, item.id)
        for item in context.document.registry.anatomy.values()
        if item.id != target and geometry_asset(item)
    ]


def check(context: Any, scope: str, cancel: Any) -> tuple[Issue, ...]:
    target, stage = scope.rsplit(":", 1)
    surface = inspection_surfaces.get(context, target, stage)
    others = neighbors(context, target)
    scan = inspection.findings(
        surface.mesh(context),
        surface.frame,
        [s.mesh(context) for s in others],
        [s.frame for s in others],
        LIMIT,
        cancel.handle,
    )
    return findings(context, scope, surface, others, scan)


def findings(context: Any, scope: str, surface: Any, others: Any, scan: Any) -> tuple[Issue, ...]:
    stamp = fingerprint(source(context.document, scope))
    ids, boxes, truncated = scan
    rows = [
        finding(context, scope, stamp, surface, others, row, box, i)
        for i, (row, box) in enumerate(zip(ids, boxes, strict=True))
    ]
    if truncated:
        rows.append(limit_finding(scope, stamp, surface))
    return tuple(rows)


def finding(
    context: Any,
    scope: str,
    stamp: str,
    surface: Any,
    others: Any,
    row: Any,
    bounds: Any,
    index: int,
) -> Issue:
    other = others[row[1]] if row[1] >= 0 else surface
    code = {1: "DEGENERATE_FACE", 2: "SELF_CROSSING", 3: "SURFACE_CROSSING"}[row[0]]
    witness = spatial_evidence.witness(context, surface, other, row, bounds)
    fields = issue_fields(surface, other, index)
    return make_issue(scope, stamp, code, witness, fields)


def make_issue(scope: str, stamp: str, code: str, witness: Any, fields: Any) -> Issue:
    return Issue(
        NAME,
        scope,
        code,
        code.replace("_", " ").capitalize(),
        source=stamp,
        evidence=evidence(witness=witness),
        **fields,
    )


def issue_fields(surface: Any, other: Any, index: int) -> dict[str, Any]:
    return dict(
        target=surface.target,
        kind=surface.kind,
        stage=surface.stage,
        local_key=str(index),
        related=(other.target,) if other is not surface else (),
        details=tissue_geometry.LIMITATIONS + " Advisory; geometry remains unchanged.",
    )


def limit_finding(scope: str, stamp: str, surface: Any) -> Issue:
    return Issue(
        NAME,
        scope,
        "FINDING_LIMIT",
        "Geometry finding limit reached",
        target=surface.target,
        kind=surface.kind,
        stage=surface.stage,
        source=stamp,
        details="Stopped after 512 findings. Unvisited geometry is not certified clean.",
    )
