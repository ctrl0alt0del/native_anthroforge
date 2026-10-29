"""Candidate stage adapters preserve canonical buffers and explicit retained output labels."""

from dataclasses import replace
from types import SimpleNamespace
from typing import Any

from anthroforge.core.entities import IDENTITY, SCP
from anthroforge.core.inspection_layers import Layer
from anthroforge.core.tissues import TissueVCP
from anthroforge.native.construction import matrix

from . import curve_sources, reconstruction_views, replacement_reviews


def capture(session: Any, kind: str, state: Any) -> tuple[Layer, ...]:
    if kind in ("skeleton_update", "variant_review"):
        return comparison(session, state.candidate)
    if kind in ("mesh_replacement", "tissue_retarget"):
        return replacement(session, state)
    if kind == "skin_fit":
        return fitted(session, state)
    return simple(session, kind, state)


def context(session: Any, document: Any, resources: Any = None) -> Any:
    return SimpleNamespace(
        engine=session.engine,
        document=document,
        resources=resources or session.resources,
        workspace=session.workspace,
    )


def accepted(
    ctx: Any, target: str, side: str, stage: str = "final", retained: bool = False
) -> Layer:
    item = ctx.document.object(target)
    status = "retained" if retained else getattr(item.result, "status", "ready")
    try:
        value = reconstruction_views.accepted(ctx, item, stage)
    except ValueError as error:
        value = Layer(target, None, IDENTITY, "NONE", reason=str(error), status="unavailable")
    return decorate(value, item, side, stage, status)


def decorate(value: Layer, item: Any, side: str, stage: str, status: str) -> Layer:
    return replace(
        value,
        identity=f"{side}:{item.id}:{stage}",
        subject=item.id,
        side=side,
        stage=stage,
        category=category(item),
        status=status if value.resource else value.status,
    )


def category(item: Any) -> str:
    if isinstance(item, SCP):
        return "bones"
    return "tissues" if isinstance(item, TissueVCP) else "construction"


def simple(session: Any, kind: str, state: Any) -> tuple[Layer, ...]:
    ctx, value = context(session, session.document), state.asset
    item = candidate_item(kind, value)
    stage = "rest" if kind == "tissue_inflation" else "final"
    before = (accepted(ctx, state.target, "before", stage),) if state.target else ()
    resource = value.path if kind == "curve_conversion" else value.mesh
    frame = candidate_frame(session, item)
    layer = Layer(item.id, resource, frame, "PATH" if kind == "curve_conversion" else "MESH")
    after = (decorate(layer, item, "after", stage, "current"),)
    related = dependents(ctx, state.target) if state.target else ()
    support = context_layers(ctx, item, {r.subject for r in (*before, *after, *related)})
    return mirrored(ctx, (*before, *after, *related, *support))


def context_layers(ctx: Any, item: Any, included: set[str]) -> tuple[Layer, ...]:
    from anthroforge.core.attachment_references import targets

    definition = getattr(item, "primitive", None) or item
    sources = {use.curve for use in getattr(definition, "curves", ())}
    sources.update((getattr(item, "source", ""), getattr(item, "parent", "")))
    sources.update(targets(item))
    return tuple(
        accepted(ctx, key, side)
        for key in sorted(sources - included)
        if key in ctx.document.registry.records
        for side in ("before", "after")
    )


def candidate_item(kind: str, value: Any) -> Any:
    return getattr(value, dict(curve_conversion="authored", surface="surface").get(kind, "item"))


def candidate_frame(session: Any, item: Any) -> tuple[float, ...]:
    parent = curve_sources.world(session.engine, session.document, item.parent)
    return tuple(matrix(session.engine, parent, item.matrix))


def dependents(ctx: Any, target: str) -> tuple[Layer, ...]:
    from .dependencies import closure

    keys = closure(ctx.document.registry.consumers, {target}) - {target}
    return tuple(
        accepted(ctx, key, side, retained=side == "after")
        for key in sorted(keys)
        for side in ("before", "after")
    )


def replacement(session: Any, state: Any) -> tuple[Layer, ...]:
    c, before = state.asset, session.document
    after = replace(
        before,
        entities=replacement_reviews.replaced(before.entities, c.entities),
        objects=replacement_reviews.replaced(before.objects, c.objects),
    )
    resources = session.resources.snapshot()
    for name in resources.__dataclass_fields__:
        getattr(resources, name).update(getattr(c.resources, name))
    view = SimpleNamespace(
        baseline=before, document=after, resources=resources, prepared=c.prepared, changes=c.changes
    )
    return comparison(session, view, set(c.entities) | set(c.objects))


def comparison(session: Any, candidate: Any, targets: Any = None) -> tuple[Layer, ...]:
    targets = targets if targets is not None else comparison_targets(candidate)
    rows: list[Layer] = []
    for side, document in (("before", candidate.baseline), ("after", candidate.document)):
        ctx = context(session, document, candidate.resources)
        values = tuple(
            accepted(ctx, key, side, retained=retained(candidate, key, side))
            for key in sorted(targets)
            if key in document.registry.records
        )
        rows.extend(mirrored(ctx, values))
    return tuple(rows)


def comparison_targets(candidate: Any) -> set[str]:
    old, new = candidate.baseline.registry.records, candidate.document.registry.records
    return {p.owner for p in candidate.prepared} | {
        key for key, item in new.items() if item != old.get(key)
    }


def retained(candidate: Any, key: str, side: str) -> bool:
    if side == "before":
        return False
    item = candidate.document.object(key)
    previous = candidate.baseline.registry.records.get(key)
    return (
        not any(p.owner == key and p.output != "pose" for p in candidate.prepared)
        and item != previous
    )


def fitted(session: Any, state: Any) -> tuple[Layer, ...]:
    item = next(f for f in session.document.skin.fits if f.id == state.target)
    before = session.assets[item.reference].mesh
    return (
        Layer("before:skin", before, IDENTITY, side="before", subject="skin", category="skin"),
        Layer("after:skin", state.asset.mesh, IDENTITY, subject="skin", category="skin"),
    )


def mirrored(ctx: Any, layers: tuple[Layer, ...]) -> tuple[Layer, ...]:
    result = list(layers)
    for layer in layers:
        for instance in ctx.document.mirrors.instances.values():
            if instance.source != layer.subject:
                continue
            frame = matrix(ctx.engine, ctx.document.mirrors.plane(instance).frame, layer.frame)
            result.append(reflected(layer, instance, frame))
    return tuple(result)


def reflected(layer: Layer, instance: Any, frame: Any) -> Layer:
    return replace(
        layer,
        identity=f"{layer.side}:{instance.id}:{layer.stage}",
        subject=instance.id,
        frame=tuple(frame),
    )
