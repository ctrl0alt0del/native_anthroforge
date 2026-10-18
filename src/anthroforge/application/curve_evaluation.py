"""Curve input resolution separates anatomical bindings from engine-owned path evaluation."""

from dataclasses import dataclass, replace
from typing import Any

from anthroforge.core.fibers import Fiber

from . import attachment_assets, curve_sources, fiber_edit_evaluation, path_assets


@dataclass(frozen=True)
class PathEvaluation:
    asset: path_assets.PathAsset
    edited: Fiber | None = None
    attachment: attachment_assets.AttachmentAsset | None = None


def evaluate(engine: Any, document: Any, resources: Any, target: str, cancel: int) -> Any:
    item = curve_sources.source(document, target)
    if not isinstance(item, Fiber):
        return PathEvaluation(path_assets.evaluate(engine, item, cancel))
    if item.attachment_asset not in resources.attachments:
        raise ValueError("Fiber has no captured attachment field.")
    asset = resources.attachments[item.attachment_asset]
    surfaces = attachment_assets.surface_inputs(engine, document, resources.meshes, asset.targets)
    world = curve_sources.world(engine, document, target)
    if item.edit:
        return PathEvaluation(
            *fiber_edit_evaluation.evaluate(engine, item, resources, document, world, cancel)
        )
    return PathEvaluation(attachment_assets.evaluate(engine, item, asset, surfaces, world, cancel))


def adopt(session: Any, item: Any, value: PathEvaluation) -> Any:
    if value.edited is None or value.attachment is None:
        return item
    session.resources.attachments[value.edited.attachment_asset] = value.attachment
    names = ("points", "bindings", "supports", "attachment_asset", "edit")
    return replace(item, **{name: getattr(value.edited, name) for name in names})
