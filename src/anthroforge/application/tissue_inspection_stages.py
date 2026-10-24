"""Accepted stages and their actual provenance, independent of authored pending settings."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.mirroring import source
from anthroforge.core.tissues import TissueVCP

from .object_frames import Frames

STAGES = dict(
    base="Construction base", rest="Inflated rest", intrinsic="Intrinsic", final="Stacked / final"
)


def tissue(context: Any, target: str) -> TissueVCP:
    item = context.document.object(source(target))
    if not isinstance(item, TissueVCP):
        raise ValueError("Choose a tissue to inspect.")
    return item


def result(item: TissueVCP, stage: str) -> Any:
    if stage not in STAGES:
        raise ValueError("Choose base, rest, intrinsic or final.")
    return getattr(item, stage + "_result")


def material(item: TissueVCP, stage: str) -> Any:
    return getattr(item, stage + "_material", None)


def describe(context: Any, target: str) -> dict[str, Any]:
    item = tissue(context, target)
    return dict(
        target=target, source=item.source, stages=[row(context, item, s, target) for s in STAGES]
    )


def row(context: Any, item: TissueVCP, stage: str, target: str = "") -> dict[str, Any]:
    value = result(item, stage)
    resource = context.resources.meshes.get(value.asset) or context.resources.paths.get(value.asset)
    kind = "MESH" if value.asset in context.resources.meshes else "PATH" if resource else "POINT"
    available = bool(resource) or (stage == "base" and item.base_state.kind == "POINT")
    return dict(
        stage=stage,
        label=STAGES[stage],
        result=asdict(value),
        available=available,
        kind=kind,
        base=base_asset(item, stage),
        frame=instance_frame(context, target or item.id, stage),
    )


def base_asset(item: TissueVCP, stage: str) -> str:
    state = material(item, stage)
    return state.base if state else item.base_result.asset


def frame(context: Any, item: TissueVCP, stage: str) -> tuple[float, ...]:
    # Results are tissue-local. Object pose is resolved separately from evaluation.
    from anthroforge.native.construction import matrix

    world = Frames(context.engine, context.document).world(item.id)
    if stage == "base" and item.base_state.kind in ("POINT", "CURVE"):
        world = matrix(context.engine, world, item.base_state.frame)
    return tuple(world)


def mesh(context: Any, target: str, stage: str) -> Any:
    value = result(tissue(context, target), stage)
    if value.asset not in context.resources.meshes:
        raise ValueError(
            STAGES[stage] + " has no accepted mesh; choose an available surface stage."
        )
    return context.resources.meshes[value.asset].mesh


def instance_frame(context: Any, target: str, stage: str) -> Any:
    from anthroforge.core.mirroring import parse
    from anthroforge.core.surface_references import SurfaceReference

    from .mirror_surfaces import frame as spatial_frame

    item = tissue(context, target)
    value = frame(context, item, stage)
    instance = parse(target)
    if not instance:
        return value
    if target not in context.document.mirrors.instances:
        raise ValueError("This mirrored tissue instance is unavailable.")
    ref = SurfaceReference(item.id, "TISSUE_FINAL", instance.rule)
    return spatial_frame(context.engine, context.document, ref, value)


def signature(context: Any, target: str, stage: str) -> Any:
    item = tissue(context, target)
    return (
        str(context.document.id),
        target,
        result(item, stage).asset,
        material(item, stage),
        instance_frame(context, target, stage),
    )


def compatible(item: TissueVCP, reference: str, stage: str) -> None:
    if stage == "base" and reference != "base":
        raise ValueError(
            "Display the inflated stage and choose Construction base as the reference. "
            "A base sample can have several inflated sides."
        )
    if base_asset(item, reference) != base_asset(item, stage):
        raise ValueError(
            "These accepted stages use different construction revisions. "
            "Evaluate dependent stages before comparing displacement."
        )
    a, b = material(item, reference), material(item, stage)
    if a and b and a.base_state != b.base_state:
        raise ValueError("These stages have different material part identities.")
