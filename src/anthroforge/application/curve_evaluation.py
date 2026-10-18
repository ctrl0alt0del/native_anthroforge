"""Curve input resolution separates anatomical bindings from engine-owned path evaluation."""

from typing import Any

from anthroforge.core.fibers import Fiber

from . import attachment_assets, curve_sources, path_assets


def evaluate(engine: Any, document: Any, resources: Any, target: str, cancel: int) -> Any:
    item = curve_sources.source(document, target)
    if not isinstance(item, Fiber):
        return path_assets.evaluate(engine, item, cancel)
    if item.attachment_asset not in resources.attachments:
        raise ValueError("Fiber has no captured attachment field.")
    asset = resources.attachments[item.attachment_asset]
    surfaces = attachment_assets.surface_inputs(engine, document, resources.meshes, asset.targets)
    world = curve_sources.world(engine, document, target)
    return attachment_assets.evaluate(engine, item, asset, surfaces, world, cancel)
