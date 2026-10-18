"""Curve input resolution separates anatomical bindings from engine-owned path evaluation."""

from dataclasses import dataclass, replace
from typing import Any

from anthroforge.core.fibers import Fiber

from . import (
    attachment_assets,
    curve_sources,
    fiber_edit_evaluation,
    path_assets,
    routing_evaluation,
)


@dataclass(frozen=True)
class PathEvaluation:
    asset: path_assets.PathAsset
    edited: Fiber | None = None
    attachment: attachment_assets.AttachmentAsset | None = None


def evaluate(engine: Any, document: Any, resources: Any, target: str, cancel: int) -> Any:
    item = curve_sources.source(document, target)
    return evaluate_item(engine, document, resources, item, cancel)


def evaluate_item(
    engine: Any, document: Any, resources: Any, item: Any, cancel: int
) -> PathEvaluation:
    if not isinstance(item, Fiber):
        return PathEvaluation(engine_path(engine, document, resources, item, cancel))
    return evaluate_fiber(engine, document, resources, item, cancel)


def evaluate_fiber(
    engine: Any, document: Any, resources: Any, item: Fiber, cancel: int
) -> PathEvaluation:
    if item.attachment_asset not in resources.attachments:
        raise ValueError("Fiber has no captured attachment field.")
    asset = resources.attachments[item.attachment_asset]
    surfaces = attachment_assets.surface_inputs(engine, document, resources.meshes, asset.targets)
    world = curve_sources.world(engine, document, item.id)
    if item.edit:
        return edited_fiber(engine, document, resources, item, world, cancel)
    resolved = attachment_assets.evaluate(engine, item, asset, surfaces, world, cancel)
    return PathEvaluation(
        engine_path(engine, document, resources, resolved.authored, cancel, resolved)
    )


def edited_fiber(
    engine: Any, document: Any, resources: Any, item: Fiber, world: Any, cancel: int
) -> PathEvaluation:
    path, changed, captured = fiber_edit_evaluation.evaluate(
        engine, item, resources, document, world, cancel
    )
    path = engine_path(engine, document, resources, changed, cancel, path)
    return PathEvaluation(path, changed, captured)


def engine_path(
    engine: Any, document: Any, resources: Any, item: Any, cancel: int, resolved: Any = None
) -> Any:
    if item.engine == "ROUTED":
        return routing_evaluation.evaluate(engine, document, resources, item, cancel, resolved)
    return resolved or path_assets.evaluate(engine, item, cancel)


def adopt(session: Any, item: Any, value: PathEvaluation) -> Any:
    if value.edited is None or value.attachment is None:
        return item
    session.resources.attachments[value.edited.attachment_asset] = value.attachment
    names = ("points", "bindings", "supports", "attachment_asset", "edit")
    return replace(item, **{name: getattr(value.edited, name) for name in names})
