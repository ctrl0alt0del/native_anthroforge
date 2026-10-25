"""Curve input resolution separates anatomical bindings from engine-owned path evaluation."""

from dataclasses import dataclass, replace
from typing import Any

from anthroforge.core.fibers import Fiber

from . import (
    attachment_assets,
    curve_sources,
    fiber_edit_evaluation,
    fiber_deformation,
    junction_bindings,
    junction_evaluation,
    parametric_evaluation,
    path_assets,
    routing_evaluation,
)


@dataclass(frozen=True)
class PathEvaluation:
    asset: path_assets.PathAsset
    edited: Fiber | None = None
    attachment: attachment_assets.AttachmentAsset | None = None


@dataclass(frozen=True)
class ResolvedCurve:
    authored: Any
    path: Any = None
    edited: Fiber | None = None
    attachment: attachment_assets.AttachmentAsset | None = None


def evaluate(
    engine: Any, document: Any, resources: Any, target: str, cancel: int, backend: str = "CUSTOM",
    propagation: str = "SMOOTH_SHAPE"
) -> Any:
    item = curve_sources.source(document, target)
    return evaluate_item(engine, document, resources, item, cancel, backend, propagation)


def evaluate_item(
    engine: Any, document: Any, resources: Any, item: Any, cancel: int, backend: str = "CUSTOM",
    propagation: str = "SMOOTH_SHAPE"
) -> PathEvaluation:
    from . import symmetric_paths

    value = resolve(engine, document, resources, item, cancel, propagation)
    path = engine_path(engine, document, resources, value, cancel, backend)
    path = symmetric_paths.expand(engine, document, item, path, cancel)
    return PathEvaluation(path, value.edited, value.attachment)


def resolve(engine: Any, document: Any, resources: Any, item: Any, cancel: int,
            propagation: str = "SMOOTH_SHAPE") -> ResolvedCurve:
    if item.engine == "PARAMETRIC":
        return resolve_parametric(engine, document, resources, item, cancel)
    value = (
        resolve_fiber(engine, document, resources, item, cancel, propagation)
        if isinstance(item, Fiber)
        else ResolvedCurve(item)
    )
    item, path = junction_evaluation.resolved(
        engine, document, resources, value.authored, cancel, value.path
    )
    return replace(value, authored=item, path=path)


def resolve_parametric(
    engine: Any, document: Any, resources: Any, item: Any, cancel: int
) -> ResolvedCurve:
    from .parametric_junctions import validate

    asset = parametric_evaluation.evaluate(engine, item, cancel)
    validate(engine, document, resources, asset.authored)
    return ResolvedCurve(asset.authored, asset)


def resolve_fiber(
    engine: Any, document: Any, resources: Any, item: Fiber, cancel: int, propagation: str
) -> ResolvedCurve:
    item = junction_bindings.resolve(document, resources, item)
    if item.attachment_asset not in resources.attachments:
        raise ValueError("Fiber has no captured attachment field.")
    asset = resources.attachments[item.attachment_asset]
    world = curve_sources.world(engine, document, item.id)
    if item.edit:
        return edited_fiber(engine, document, resources, item, world, cancel, propagation)
    positions = fiber_deformation.resolve(engine, document, resources, item, asset, cancel, propagation)
    resolved = attachment_assets.evaluate(engine, item, asset, positions, world, cancel)
    return ResolvedCurve(resolved.authored, resolved)


def edited_fiber(
    engine: Any, document: Any, resources: Any, item: Fiber, world: Any, cancel: int, propagation: str
) -> ResolvedCurve:
    path, changed, captured = fiber_edit_evaluation.evaluate(
        engine, item, resources, document, world, cancel, propagation
    )
    return ResolvedCurve(changed, path, changed, captured)


def engine_path(
    engine: Any, document: Any, resources: Any, value: ResolvedCurve, cancel: int, backend: str
) -> Any:
    item, resolved = value.authored, value.path
    if item.engine == "ROUTED":
        return routing_evaluation.evaluate(
            engine, document, resources, item, cancel, resolved, backend
        )
    return resolved or path_assets.evaluate(engine, item, cancel)


def adopt(session: Any, item: Any, value: PathEvaluation) -> Any:
    if item.engine == "PARAMETRIC":
        return replace(item, points=value.asset.authored.points)
    if value.edited is None or value.attachment is None:
        return item
    session.resources.attachments[value.edited.attachment_asset] = value.attachment
    names = ("points", "bindings", "supports", "attachment_asset", "edit")
    return replace(item, **{name: getattr(value.edited, name) for name in names})
